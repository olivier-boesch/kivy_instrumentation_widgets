import _compat  # noqa: F401  (shim de compatibilité Python 3.14+)

import random
from datetime import timedelta

from kivy.config import Config

Config.set('graphics', 'width', '1280')
Config.set('graphics', 'height', '800')

from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty

import theme
from units import ureg
from jauge import CircularGauge
from rollingchart import RollingChart
from valuepopup import UnitNumberPopup

Window.clearcolor = theme.BACKGROUND


def encoder_side(size, n=2):
    """Côté (carré) de chaque encodeur pour remplir l'espace disponible du panneau."""
    w, h = size
    spacing = dp(20)
    return max(0.0, min(h, (w - spacing * (n - 1)) / n))


KV = '''
#:import theme theme
#:import timedelta datetime.timedelta
#:import FlatButton flatbutton.FlatButton
#:import FlatToggleButton flatbutton.FlatToggleButton
#:import BorderWrapper borderwrapper.BorderWrapper
#:import CircularTimer timer.CircularTimer
#:import ValidationWidget validationwidget.ValidationWidget
#:import RotaryEncoderWidget encoder.RotaryEncoderWidget
#:import SliderWidget sliderwidget.SliderWidget
#:import encoder_side demo.encoder_side

BoxLayout:
    orientation: 'vertical'
    padding: dp(15)
    spacing: dp(15)

    BoxLayout:
        size_hint_y: None
        height: dp(40)
        spacing: dp(15)

        Label:
            text: "Kivy Instrumentation Widgets — Démo"
            color: theme.TEXT
            font_size: dp(22)
            bold: True

        FlatButton:
            text: app.theme_button_text
            size_hint_x: None
            width: dp(160)
            on_press: app.toggle_theme()

    BoxLayout:
        orientation: 'horizontal'
        spacing: dp(15)

        # --- Colonne 1 : jauge circulaire + minuteur ---
        BoxLayout:
            orientation: 'vertical'
            spacing: dp(15)
            size_hint_x: 0.28

            BorderWrapper:
                id: gauge_wrap
                title: "Puissance"
                padding: dp(20)
                radius: dp(20)

            BorderWrapper:
                title: "Minuteur"
                padding: dp(20)
                radius: dp(20)
                orientation: 'vertical'
                spacing: dp(10)

                CircularTimer:
                    id: timer

                BoxLayout:
                    size_hint_y: None
                    height: dp(44)
                    spacing: dp(10)

                    FlatButton:
                        text: "Start (1 min)"
                        on_press: timer.start(timedelta(minutes=1))
                    FlatButton:
                        text: "Pause"
                        on_press: timer.pause()
                    FlatButton:
                        text: "Stop"
                        on_press: timer.stop()

        # --- Colonne 2 : graphique, validation et boutons ---
        BoxLayout:
            orientation: 'vertical'
            spacing: dp(15)
            size_hint_x: 0.42

            BorderWrapper:
                id: chart_wrap
                title: "Mesure"
                padding: dp(20)
                radius: dp(20)
                orientation: 'vertical'
                spacing: dp(10)

                FlatButton:
                    text: "Injecter mesure aléatoire"
                    size_hint_y: None
                    height: dp(44)
                    on_press: app.inject_measure()

            BorderWrapper:
                title: "Validation"
                padding: dp(20)
                radius: dp(20)
                size_hint_y: None
                height: dp(120)

                ValidationWidget:
                    id: validation
                    slider_text: "Arm >"
                    slider_text_armed: "< Annuler"
                    button_text: "OK"
                    on_press: app.on_validation_press(self)

            BorderWrapper:
                title: "Boutons plats"
                padding: dp(20)
                radius: dp(20)
                orientation: 'vertical'
                spacing: dp(10)
                size_hint_y: None
                height: dp(150)

                BoxLayout:
                    size_hint_y: None
                    height: dp(44)
                    spacing: dp(10)

                    FlatButton:
                        text: "Valider"
                    FlatButton:
                        text: "Annuler"

                BoxLayout:
                    size_hint_y: None
                    height: dp(44)
                    spacing: dp(10)

                    FlatToggleButton:
                        text: "Auto"
                        group: "mode"
                    FlatToggleButton:
                        text: "Manuel"
                        group: "mode"

        # --- Colonne 3 : encodeurs rotatifs + sliders ---
        BoxLayout:
            orientation: 'vertical'
            spacing: dp(15)
            size_hint_x: 0.30

            BorderWrapper:
                title: "Réglages"
                padding: dp(20)
                radius: dp(20)

                AnchorLayout:
                    id: encoders_anchor

                    BoxLayout:
                        size_hint: None, None
                        spacing: dp(20)
                        size: encoder_side(encoders_anchor.size) * 2 + dp(20), encoder_side(encoders_anchor.size)

                        RotaryEncoderWidget:
                            size_hint: None, None
                            size: encoder_side(encoders_anchor.size), encoder_side(encoders_anchor.size)
                            min_value: 0
                            max_value: 100
                            granularity: 0.01
                            step_max_multiplier: 30
                            unit: 'W'
                            quantity_name: "Puissance"

                        RotaryEncoderWidget:
                            size_hint: None, None
                            size: encoder_side(encoders_anchor.size), encoder_side(encoders_anchor.size)
                            min_value: 0
                            max_value: 10
                            granularity: 0.01
                            unit: 'A'
                            quantity_name: "Courant"

            BorderWrapper:
                title: "Sliders"
                padding: dp(20)
                radius: dp(20)

                AnchorLayout:
                    BoxLayout:
                        orientation: 'vertical'
                        spacing: dp(10)
                        size_hint: 1, None
                        height: dp(130)

                        SliderWidget:
                            id: slider_speed
                            size_hint_y: None
                            height: dp(60)
                            min_value: 0
                            max_value: 100
                            granularity: 0.1
                            unit: 'm/s'
                            quantity_name: "Vitesse"
                            on_label_press: app.open_popup(self)

                        SliderWidget:
                            id: slider_power
                            size_hint_y: None
                            height: dp(60)
                            min_value: 0
                            max_value: 10
                            granularity: 5
                            unit: 'W'
                            quantity_name: "Puissance"
                            on_label_press: app.open_popup(self)
'''


class DemoApp(App):
    """Tableau de bord présentant tous les widgets du paquet."""

    theme_button_text = StringProperty("Thème clair")

    def build(self):
        self.popup = UnitNumberPopup()
        self._gauge_event = None
        self._chart_event = None
        return self._build_root()

    def _build_root(self):
        root = Builder.load_string(KV)

        self.gauge = CircularGauge(min_value=0 * ureg.watt, max_value=50 * ureg.watt, window_size_n=10)
        root.ids.gauge_wrap.add_widget(self.gauge)

        self.chart = RollingChart(y_unit=0 * ureg.watt, x_step=1 * ureg.second, x_window=100)
        root.ids.chart_wrap.add_widget(self.chart, index=1)

        self.timer = root.ids.timer

        return root

    def on_start(self):
        self._start_clocks()

    def _start_clocks(self):
        self.timer.start(timedelta(minutes=1))

        self.gauge.set_value(25 * ureg.watt)
        self._gauge_event = Clock.schedule_interval(
            lambda dt: self.gauge.set_value(
                self.gauge.current_value + random.uniform(-5, 5) * ureg.watt
            ),
            1,
        )

        self._chart_value = 50.0

        def tick(dt):
            self._chart_value = max(0, min(50, self._chart_value + random.uniform(-3, 3)))
            self.chart.push(self._chart_value * ureg.watt)

        self._chart_event = Clock.schedule_interval(tick, 1 / 30)

    def toggle_theme(self):
        self._gauge_event.cancel()
        self._chart_event.cancel()

        new_theme = theme.LIGHT if theme.get_theme() is theme.DARK else theme.DARK
        theme.set_theme(new_theme)
        self.theme_button_text = "Thème sombre" if new_theme is theme.LIGHT else "Thème clair"
        Window.clearcolor = theme.BACKGROUND

        old_root = self.root
        self.root = self._build_root()
        self.root_window.remove_widget(old_root)
        self.root_window.add_widget(self.root)

        self._start_clocks()

    def inject_measure(self):
        self.chart.push(random.uniform(0, 50) * ureg.watt)

    def on_validation_press(self, instance):
        print("Validation déclenchée")

    def open_popup(self, slider):
        self.popup.open(
            current_value=slider.value,
            callback=lambda q: slider.set_value(q.to(slider._unit).magnitude),
            title=slider.quantity_name or "Valeur",
        )


if __name__ == '__main__':
    DemoApp().run()
