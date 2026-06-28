import qsharp
from aval_backend import ensure_qsharp_initialized, branch_obj_to_dict, BranchModel

print('Ensure Q# init...')
ensure_qsharp_initialized()
print('Calling Q# SampleBranchWeighted...')
res = qsharp.run('AVALYOS.Quantum.SampleBranchWeighted()', shots=1)
print('Raw result repr:', repr(res))
raw = res[0] if isinstance(res, list) and len(res)>0 else res
print('Raw element repr:', repr(raw))
bd = branch_obj_to_dict(raw)
print('Converted dict:', bd)
model = BranchModel(**bd)
print('Pydantic model:', model.json(indent=2))
