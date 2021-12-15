/**
@typedef {{
  dual_x_div_style: Object
  path: string
  size: string
  changes: [string, string|number, string|number][]
  statistics: [string, string, string][]
  commit: number
  line: number
  lineChanges: number
}} MyThis

@typedef {{
  path: MyThis["path"]
  size: MyThis["size"]
}} MyLocaleStorage

@typedef {{
  changes: MyThis["changes"]
  statistics: MyThis["statistics"]
  commit: MyThis["commit"]
  line: MyThis["line"]
  lineChanges: MyThis["lineChanges"]
}} MyResponse
*/
