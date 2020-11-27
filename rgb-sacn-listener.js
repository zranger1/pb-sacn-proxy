export var pixels = array(pixelCount)

export function render(index) {
  var p = pixels[index]
  r = (p >> 8) & 0xff; g = p & 0xff; b = (p * 256 + .5) & 0xff
  rgb(r, g, b)
}