import _compat  # noqa: F401  (shim de compatibilité Python 3.14+)

from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.behaviors import FocusBehavior
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, ListProperty
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Line, Ellipse

from units import ureg
from theme import ACCENT, ACCENT_DIM, TEXT, EDIT
from granularity import snap_value, format_value

__all__ = ['SliderWidget']

Builder.load_string("""
#:import theme theme
#:import FlatButton flatbutton
<SliderWidget>:
    graphics_color: theme.ACCENT
    text_color: theme.TEXT

    BoxLayout:
        orientation: 'horizontal'
        pos: root.pos
        size: root.size
        padding: dp(12)
        spacing: dp(12)

        Widget:
            id: track
            size_hint_x: 0.7

        FlatButton:
            id: value_label
            size_hint_x: 0.3
            button_color: root.graphics_color
            color: root.text_color
            font_size: min(self.height, self.width * 0.4) * 0.3
            text:
                (root.quantity_name + chr(10) if root.quantity_name else '') \
                + root.value_text \
                + (' ' + root.unit_text if root.unit_text else '')
            on_release: root.dispatch('on_label_press')
""")


class SliderWidget(FocusBehavior, Widget):
    """Slider horizontal personnalisé avec affichage de la valeur à droite.

    Contrairement à un `kivy.uix.slider.Slider`, ce widget dessine lui-même
    sa piste et son curseur, et expose un label de valeur cliquable et un
    contrôle au clavier (le tout dans le style visuel des autres widgets).

    Propriétés KV :
        min_value      (float) — valeur minimale (extrémité gauche)
        max_value      (float) — valeur maximale (extrémité droite)
        unit           (str)   — unité Pint (ex. 'W', 'A', 'm/s')
        quantity_name  (str)   — libellé affiché au-dessus de la valeur
        granularity    (float) — pas de quantification de la valeur (voir
                                  `granularity.py`) ; `None` désactive l'arrondi
                                  et vaut alors 1 pour les flèches clavier
        graphics_color (list)  — couleur RGBA de la piste / du curseur
        text_color     (list)  — couleur RGBA du texte

    Interactions :
        glisser      — déplace le curseur sur la piste et met à jour la valeur
        clic/tap     — donne le focus clavier au widget (bordure orange)
        flèches ←/→  — incrémente/décrémente la valeur de `granularity`
        Page Haut/Bas — incrémente/décrémente la valeur de `10 * granularity`
        Origine/Fin  — règle la valeur sur `min_value` / `max_value`
        label valeur — émet `on_label_press` (à connecter par exemple à
                       `UnitNumberPopup` pour une saisie numérique directe)
    """

    min_value = NumericProperty(0)
    max_value = NumericProperty(100)
    value     = ObjectProperty(None)
    unit      = ObjectProperty(None)

    value_text    = StringProperty("")
    unit_text     = StringProperty("")
    quantity_name = StringProperty("")
    granularity   = NumericProperty(0.01, allownone=True)

    graphics_color = ListProperty(ACCENT)
    text_color     = ListProperty(TEXT)

    __events__ = ('on_label_press',)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._unit     = None
        self._x_min    = 0.0
        self._x_max    = 0.0
        self._track_y  = 0.0
        self._handle_r = dp(10)

        with self.canvas:
            self._focus_color = Color(*EDIT[:3], 0)
            self._focus_border = Line(width=dp(1.5))

            Color(*ACCENT_DIM)
            self._bg_line = Line(width=dp(4), cap='round')

            self._fg_color = Color(*self.graphics_color)
            self._fg_line = Line(width=dp(4), cap='round')

            self._handle_color = Color(*self.graphics_color)
            self._handle = Ellipse()

        self.bind(
            pos=self._rebuild_geometry,
            size=self._rebuild_geometry,
            value=self._on_value_changed,
            graphics_color=self._update_color,
            unit=self._on_unit_change,
            focus=self._update_focus,
        )
        self._rebuild_geometry()
        Clock.schedule_once(self._deferred_init, 0)

    def on_label_press(self, *_):
        pass

    def on_kv_post(self, base_widget):
        self.ids.track.bind(pos=self._rebuild_geometry, size=self._rebuild_geometry)

    # ------------------------------------------------------------------
    # Initialisation et mise à jour de l'unité
    # ------------------------------------------------------------------

    def _deferred_init(self, _):
        self._unit = ureg(self.unit)
        if self.value is None:
            self.value = self.min_value * self._unit
        self.update_text()
        self._rebuild_geometry()

    def _on_unit_change(self, *_):
        if self.unit:
            self._unit = ureg(self.unit)
        self.update_text()

    # ------------------------------------------------------------------
    # Canvas
    # ------------------------------------------------------------------

    def _update_color(self, *_):
        self._fg_color.rgba = self.graphics_color
        if not self.focus:
            self._handle_color.rgba = self.graphics_color

    def _update_focus(self, *_):
        self._focus_color.a = 1 if self.focus else 0
        self._handle_color.rgba = EDIT if self.focus else self.graphics_color

    def _rebuild_geometry(self, *_):
        track = self.ids.get('track')
        if track is None:
            return
        self._handle_r = min(track.height, dp(24)) / 2
        self._track_y  = track.center_y
        self._x_min = track.x + self._handle_r
        self._x_max = track.right - self._handle_r

        self._focus_border.rounded_rectangle = (*self.pos, *self.size, dp(8))

        if self._x_max <= self._x_min:
            return
        self._bg_line.points = [self._x_min, self._track_y, self._x_max, self._track_y]
        self._update_handle()

    def _update_handle(self, *_):
        if self._x_max <= self._x_min or self.value is None:
            return
        frac = self._value_fraction()
        x = self._x_min + frac * (self._x_max - self._x_min)
        self._fg_line.points = [self._x_min, self._track_y, x, self._track_y]
        d = self._handle_r * 2
        self._handle.pos  = (x - self._handle_r, self._track_y - self._handle_r)
        self._handle.size = (d, d)

    def _value_fraction(self):
        span = self.max_value - self.min_value
        if span == 0:
            return 0.0
        frac = (self.value.magnitude - self.min_value) / span
        return max(0.0, min(1.0, frac))

    # ------------------------------------------------------------------
    # Texte
    # ------------------------------------------------------------------

    def _on_value_changed(self, *_):
        self.update_text()
        self._update_handle()

    def update_text(self, *_):
        if self.value is None:
            return
        self.value_text = format_value(self.value.magnitude, self.granularity)
        self.unit_text  = f"{self.value.units:~^P}"

    # ------------------------------------------------------------------
    # Valeur
    # ------------------------------------------------------------------

    def set_value(self, magnitude):
        """Règle la valeur (grandeur brute) en la bornant et l'arrondissant.

        Utilisable comme callback de `UnitNumberPopup` une fois converti :
        `slider.set_value(quantity.to(slider._unit).magnitude)`.
        """
        magnitude = snap_value(max(self.min_value, min(self.max_value, magnitude)), self.granularity)
        self.value = magnitude * self._unit

    # ------------------------------------------------------------------
    # Touch
    # ------------------------------------------------------------------

    def _set_value_from_x(self, x):
        if self._x_max <= self._x_min:
            return
        frac = (x - self._x_min) / (self._x_max - self._x_min)
        frac = max(0.0, min(1.0, frac))
        self.set_value(self.min_value + frac * (self.max_value - self.min_value))

    def on_touch_down(self, touch):
        if not self.ids.track.collide_point(*touch.pos):
            return super().on_touch_down(touch)
        self.focus = True
        touch.grab(self)
        self._set_value_from_x(touch.x)
        return True

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return super().on_touch_move(touch)
        self._set_value_from_x(touch.x)
        return True

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return super().on_touch_up(touch)
        touch.ungrab(self)
        return True

    # ------------------------------------------------------------------
    # Clavier
    # ------------------------------------------------------------------

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        key = keycode[1]
        step = self.granularity if self.granularity else 1
        if key == 'left':
            self.set_value(self.value.magnitude - step)
        elif key == 'right':
            self.set_value(self.value.magnitude + step)
        elif key == 'pagedown':
            self.set_value(self.value.magnitude - step * 10)
        elif key == 'pageup':
            self.set_value(self.value.magnitude + step * 10)
        elif key == 'home':
            self.set_value(self.min_value)
        elif key == 'end':
            self.set_value(self.max_value)
        else:
            return super().keyboard_on_key_down(window, keycode, text, modifiers)
        return True


if __name__ == '__main__':
    from kivy.app import App
    from borderwrapper import BorderWrapper
    from valuepopup import UnitNumberPopup

    kv_app = """
BoxLayout:
    orientation: 'vertical'
    padding: dp(20)
    spacing: dp(10)

    Label:
        text: "Slider"
        font_size: dp(22)
        halign: 'center'
        size_hint_y: 0.15

    BorderWrapper:
        title: "Vitesse"
        padding: dp(20)
        radius: dp(20)
        SliderWidget:
            id: slider_speed
            min_value: 0
            max_value: 100
            granularity: 0.1
            unit: 'm/s'
            quantity_name: "Vitesse"

    BorderWrapper:
        title: "Puissance"
        padding: dp(20)
        radius: dp(20)
        SliderWidget:
            id: slider_power
            min_value: 0
            max_value: 10
            unit: 'W'
            granularity: 5
            quantity_name: "Puissance"
"""

    class SliderApp(App):
        def build(self):
            self.popup = UnitNumberPopup()
            root = Builder.load_string(kv_app)
            for slider in (root.ids.slider_speed, root.ids.slider_power):
                slider.bind(on_label_press=self.open_popup)
            return root

        def open_popup(self, slider):
            self.popup.open(
                current_value=slider.value,
                callback=lambda q: slider.set_value(q.to(slider._unit).magnitude),
                title=slider.quantity_name or "Valeur",
            )

    SliderApp().run()
