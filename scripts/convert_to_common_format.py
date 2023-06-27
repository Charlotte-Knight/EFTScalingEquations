import json
import sys
import os
import numpy as np
import copy

class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def getCoefficients(eqns):
  coefficients = set()
  for name, eqn in eqns.items():
    for key in eqn.keys():
      key = key.replace("u_", "")
      cs = key.split("_")[1:]
      if "2" in cs:
        cs.remove("2")
      coefficients.update(cs)

  return list(coefficients)

def createDataBlock(coefficients, n_obserables):
  block = {}

  for i, ci in enumerate(coefficients):
    block[f"a_{ci}"] = np.zeros(n_obserables)
  
  for i, ci in enumerate(coefficients):
    for j, cj in enumerate(coefficients):
      if j >= i:
        block[f"b_{ci}_{cj}"] = np.zeros(n_obserables)

  return block

def getSkeleton(eqns):
  coefficients = getCoefficients(eqns)
  observable_names = list(eqns.keys())

  data = {"central": createDataBlock(coefficients, len(observable_names)),
          "u_MC": createDataBlock(coefficients, len(observable_names))}

  for k, name in enumerate(observable_names):
    print(name)
    eqn = eqns[name]

    for i, ci in enumerate(coefficients):
      has_lin_term = f"A_{ci}" in eqn.keys()
      has_quad_term = f"B_{ci}_2" in eqn.keys()

      if has_lin_term:
        has_linear_term = True
        data["central"][f"a_{ci}"][k] = eqn[f"A_{ci}"]
        if f"u_A_{ci}" in eqn.keys():
          data["u_MC"][f"a_{ci}"][k] = eqn[f"u_A_{ci}"]

      if has_quad_term:
        data["central"][f"b_{ci}_{ci}"][k] = eqn[f"B_{ci}_2"]
        if f"u_B_{ci}_2" in eqn.keys():
          data["u_MC"][f"b_{ci}_{ci}"][k] = eqn[f"u_B_{ci}_2"]

      if has_lin_term ^ has_quad_term:
        print(f"WARNING: {ci} only has a lin or quad term (not both)")


      for j, cj in enumerate(coefficients):
        if f"B_{ci}_{cj}" in eqn.keys():
          if j > i:
            data["central"][f"b_{ci}_{cj}"][k] = eqn[f"B_{ci}_{cj}"]
            if f"u_B_{ci}_{cj}" in eqn.keys():
              data["u_MC"][f"b_{ci}_{cj}"][k] = eqn[f"u_B_{ci}_{cj}"]
          else:
            data["central"][f"b_{cj}_{ci}"][k] = eqn[f"B_{ci}_{cj}"]
            if f"u_B_{ci}_{cj}" in eqn.keys():
              data["u_MC"][f"b_{cj}_{ci}"][k] = eqn[f"u_B_{ci}_{cj}"]

  row_names = data["central"].keys()
  row_names_to_remove = []
  for name in row_names:
    to_compare = []
    for i, block in data.items():
      to_compare.append(block[name])

    if np.sum(to_compare) == 0:
      row_names_to_remove.append(name)

  for name in row_names_to_remove:
    for i, block in data.items():
      del block[name]

  skeleton = {"metadata": {"coefficients":  coefficients, "observable_shape": str(np.array(observable_names).shape), "observable_names": observable_names},
              "data": data}

  return skeleton

def removeIndentInLists(json_str):
  new_str = ""
  in_list = 0
  for char in json_str:
    if char == "[":
      in_list += 1
    elif char == "]":
      in_list -= 1

    if (char != "\n") or (in_list == 0):
      new_str += char
    
  return new_str

indir = sys.argv[1]
outdir = sys.argv[2]
assert indir != outdir

os.makedirs(outdir, exist_ok=True)

with open(os.path.join(indir, "prod.json"), "r") as f:
  prod_eqns = json.load(f)
with open(os.path.join(indir, "decay.json"), "r") as f:
  decay_eqns = json.load(f)

stage0 = set()
for key in prod_eqns:
  stage0.add(key.split("_")[0])
print(prod_eqns.keys())
print(stage0)

extra_metadata = {
  "author": "Matthew Knight",
  "contact": "matthew.knight@cern.ch",
  "date [DD/MM/YY]": "22/06/2023",
  "description": "",
  "documentation": ["https://github.com/MatthewDKnight/EFT2Obs/tree/Run2Legacy/cards"],
  "tool_version": "MG5_aMC_v2_6_7",
  "UFO": "SMEFTsim_topU3l_MwScheme_UFO",
  "flavor_scheme": "topU3l",
  "inputs":{
    "Lambda": 1000,
    "MW": 80.379,
    "MW": 91.1876,
    "GF": 1.16638e-5,
    "aS": 0.1181,
    "MH": 125.0,
    "MB": 3.237,
    "MT": 173.2
  },
  "EW_input_scheme": "MW_MZ_GF",
  "EFT_order": "quadratic",
  "pertubative_order_QCD": "LO",
  "pertubative_order_QED/EW": "LO",
  "method" : "reweighting"
}

for stage0_proc in stage0:
  prod_skeleton = getSkeleton({key:prod_eqns[key] for key in prod_eqns if key.split("_")[0] == stage0_proc})
  prod_skeleton["metadata"].update(copy.deepcopy(extra_metadata))
  prod_skeleton["metadata"]["PDF"] = "NNPDF31_nnlo_hessian_pdfas [306000]"

  if stage0_proc in ["GG2H", "GG2HLL"]:
    prod_skeleton["metadata"]["UFO"] = "SMEFTatNLO"
    prod_skeleton["metadata"]["flavor_scheme"] = "SMEFTatNLO"
  if stage0_proc == "GG2H":
    prod_skeleton["scale_choice"] = "125 GeV"
  elif stage0_proc == "GG2HLL":
    prod_skeleton["scale_choice"] = "108 GeV"

  json_str = json.dumps(prod_skeleton, indent=1, cls=NumpyEncoder)
  with open(os.path.join(outdir, f"{stage0_proc}.json"), "w") as f:
    f.write(removeIndentInLists(json_str))



for key in decay_eqns:
  prod_skeleton = getSkeleton({key:decay_eqns[key]})
  prod_skeleton["metadata"].update(copy.deepcopy(extra_metadata))

  if key in ["gamgam", "Zgam"]:
    del prod_skeleton["metadata"]["UFO"]
    del prod_skeleton["data"]["u_MC"]
    prod_skeleton["metadata"]["pertubative_order_QED/EW"] = "NLO"
    prod_skeleton["metadata"]["method"] = "analytic"

  if key == "gamgam":
    prod_skeleton["metadata"]["documentation"].append("https://arxiv.org/abs/1807.11504")
  elif key == "Zgam":
    prod_skeleton["metadata"]["documentation"].append("https://arxiv.org/abs/1801.01136")

  if key == "tot":
    prod_skeleton["metadata"]["method"] = "reweighting/direct"

  json_str = json.dumps(prod_skeleton, indent=1, cls=NumpyEncoder)
  with open(os.path.join(outdir, f"{key}.json"), "w") as f:
    f.write(removeIndentInLists(json_str))

