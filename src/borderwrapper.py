import _compat  # noqa: F401  (shim de compatibilité Python 3.14+)

__all__ = ['BorderWrapper']

from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty, NumericProperty, ObjectProperty
from kivy.graphics import Color, Line, Rectangle, StencilPush, StencilPop, StencilUse, StencilUnUse
from kivy.metrics import dp

from theme import ACCENT_DIM, TEXT
from _canvas_utils import make_texture


class BorderWrapper(BoxLayout):
    """BoxLayout avec bordure arrondie et titre en incrustation.

    Propriétés KV :
        title        (str)   — texte du titre affiché en haut de la bordure
        title_color  (list)  — couleur RGBA du titre
        border_color (list)  — couleur RGBA de la bordure
        border_width (float) — épaisseur de la bordure en dp
        radius       (float) — rayon des coins arrondis en dp
    """

    title        = StringProperty("")
    title_color  = ListProperty(TEXT)
    border_color = ListProperty(ACCENT_DIM)
    border_width = NumericProperty(1.5)
    radius       = NumericProperty(8)
    title_texture = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dp10 = dp(10)
        self._dp20 = dp(20)

        with self.canvas.before:
            StencilPush()
            self._smask_bot   = Rectangle()
            self._smask_left  = Rectangle()
            self._smask_right = Rectangle()
            StencilUse()
            self._border_color_instr = Color(*self.border_color)
            self._border_line = Line(width=dp(self.border_width))
            StencilUnUse()
            StencilPop()

        with self.canvas.after:
            self._title_color_instr = Color(*TEXT[:3], 0)
            self._title_rect = Rectangle()

        self.bind(
            title=self._update_texture,
            title_color=self._update_texture,
            padding=self._update_texture,
            pos=self._rebuild_canvas,
            size=self._rebuild_canvas,
            title_texture=self._rebuild_canvas,
            border_color=self._on_border_color,
            border_width=self._on_border_width,
            radius=self._rebuild_canvas,
        )
        self._update_texture()

    def _on_border_color(self, *_):
        self._border_color_instr.rgba = self.border_color

    def _on_border_width(self, *_):
        self._border_line.width = dp(self.border_width)

    def _rebuild_canvas(self, *_):
        x, y, w, h = self.x, self.y, self.width, self.height
        r  = dp(self.radius)
        tt = self.title_texture

        self._border_line.rounded_rectangle = (x, y, w, h, r)

        if tt:
            tw, th   = tt.width, tt.height
            title_y  = self.top - th / 2
            d10, d20 = self._dp10, self._dp20

            self._smask_bot.pos   = (x, y);             self._smask_bot.size  = (w, title_y - y)
            self._smask_left.pos  = (x, title_y);       self._smask_left.size = (r + d10, th)
            self._smask_right.pos = (x + r + tw + d20, title_y)
            self._smask_right.size = (self.right - (x + r + tw + d20), th)

            self._title_color_instr.rgba = TEXT
            self._title_rect.texture = tt
            self._title_rect.pos  = (x + r + d10, title_y)
            self._title_rect.size = tt.size
        else:
            self._smask_bot.pos  = (x, y); self._smask_bot.size  = (w, h)
            self._smask_left.size  = (0, 0)
            self._smask_right.size = (0, 0)
            self._title_color_instr.a = 0
            self._title_rect.size = (0, 0)

    def _update_texture(self, *_):
        if self.title:
            self.title_texture = make_texture(
                self.title, self.padding[1], self.title_color, bold=True,
                halign='center', padding=[self._dp10, 0, self._dp10, 0],
            )
        else:
            self.title_texture = None
