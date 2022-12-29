import re

def m21_to_mto_label(note: str) -> str:
  """
  Convert an a music21 note to an mto note.
  mto notes use Flat instead of - and Sharp instead
  of #.

  Args:
      note (str): Note in music21 format
  Returns:
      str: Note in mto format.
  """
  NUMBER_RE = re.compile(r"\d")
  note = NUMBER_RE.sub("", note)
  if "bb" in note: 
    note = note.replace("bb", "DoubleFlat")
  elif "##" in note: 
    note = note.replace("##", "DoubleSharp")
  elif "b" in note: 
    note = note.replace("b", "Flat")
  elif "#" in note: 
    note = note.replace("#", "Sharp")
  return note

def m21_to_leadsheet_label(note: str) -> str:
  """
  Convert an a music21 note to a leadsheet note.
  
  Args:
      note (str): Note in music21 format
  Returns:
      str: Note in mto format.
  """
  note = note.replace("-", "b")
  return note
