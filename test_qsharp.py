import qsharp

print('Initializing qsharp...')
qsharp.init(project_root='.')
print('qsharp initialized')

print('\nCalling SampleBranchWeighted (shots=1)\n')
try:
    res = qsharp.run('AVALYOS.Quantum.SampleBranchWeighted()', shots=1)
    print('Result (raw):', repr(res))
    if isinstance(res, list) and len(res) > 0:
        print('First element repr:', repr(res[0]))
except Exception as e:
    print('Error calling SampleBranchWeighted:', type(e), e)

print('\nCalling GetSampleBranches (shots=1)\n')
try:
    res2 = qsharp.run('AVALYOS.Quantum.GetSampleBranches()', shots=1)
    print('GetSampleBranches raw repr:', repr(res2))
    if isinstance(res2, list) and len(res2) > 0:
        print('First element repr:', repr(res2[0]))
        print('Len of first element if sequence:', len(list(res2[0])))
except Exception as e:
    print('Error calling GetSampleBranches:', type(e), e)
