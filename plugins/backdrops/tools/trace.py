# Traces a photo to vector shapes: python tools/trace.py <in.png> <out.svg> 10 40 4 (needs: pip install vtracer)
import sys, vtracer, re
src, dst, speckle, layer, prec = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
vtracer.convert_image_to_svg_py(src, dst, colormode="color", hierarchical="stacked", mode="spline",
    filter_speckle=speckle, color_precision=prec, layer_difference=layer, corner_threshold=60,
    length_threshold=4.0, max_iterations=10, splice_threshold=45, path_precision=1)
s = open(dst).read()
print(dst.split('/')[-1], len(s))
