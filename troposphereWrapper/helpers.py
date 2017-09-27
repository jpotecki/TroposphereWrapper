def checkForNoneValues(obj):
  if any(value is None for attr, value in vars(obj).items()):
      xs = filter(lambda x: x[1] == None, vars(obj).items())
      xs = list(map(lambda x: x[0], xs))
      raise ValueError("Values which are None: "+ str(xs))