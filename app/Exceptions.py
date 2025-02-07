class NoGlucoseDataError(Exception):
  def __init__(self):
    super().__init__('Last glucose reading is not available.')

class GlucoseFetcherNotInitialisedError(Exception):
  def __init__(self):
    super().__init__('Glucose fetcher not initialised.')
    
class DexcomApiNotInitialisedError(Exception):
  def __init__(self):
    super().__init__('Dexcom API not initialised.')