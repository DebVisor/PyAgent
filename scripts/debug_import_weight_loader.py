import importlib.util, traceback, sys
spec = importlib.util.spec_from_file_location('weight_loader','src/infrastructure/engine/loading/weight_loader.py')
mod = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(mod)
    print('import ok')
except Exception:
    traceback.print_exc()
    sys.exit(1)
