import ezdxf, sys
from ezdxf.addons.drawing import RenderContext, Frontend
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend
from ezdxf.addons.drawing.config import Configuration, BackgroundPolicy, ColorPolicy
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
doc = ezdxf.readfile('cad/Samarkand_R12-v12.1.dxf'); msp = doc.modelspace()
def shot(x0, y0, x1, y1, out, w=16):
    fig = plt.figure(figsize=(w, w * (y1 - y0) / (x1 - x0))); ax = fig.add_axes([0, 0, 1, 1])
    cfg = Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.BLACK)
    Frontend(RenderContext(doc), MatplotlibBackend(ax), config=cfg).draw_layout(msp, finalize=False)
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.axis('off'); fig.savefig(out, dpi=110); plt.close(fig)
shot(-3500, -19500, 41500, 9500, 'cad/prev_plan.png')
shot(-1000, -40500, 44500, -15500, 'cad/prev_secAB.png', 18)
shot(-2000, -62000, 45000, -15000, 'cad/prev_sec.png', 16)
shot(-2000, -160000, 32000, -134000, 'cad/prev_dev.png', 16)
