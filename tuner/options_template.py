OPTIONS_JSON_TEMPLATE = """
{
  "seconds_per_move": 5,
  "results_file_format": "xlsx",
  "options": {
    "backend": ["check"],
    "cpuct": [
      2.8,
      3.0
    ],
    "minibatch-size": [
      64,
      128
    ],
    "nncache": [
      1000000
      2000000
    ],
    "threads": [
      2,
      3
    ],
    "multipv": [
      1
    ]
  }
}
"""
