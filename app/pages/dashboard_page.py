from __future__ import annotations

from PySide6.QtCharts import QBarCategoryAxis, QBarSeries, QBarSet, QChart, QChartView, QPieSeries, QValueAxis
from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QCheckBox, QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from services.dashboard_service import franchise_news, network_efficiency, network_status_breakdown, sales_last_10_days, summary_cards


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 12, 16, 12)

        title = QLabel('Личный кабинет. Главная')
        title.setObjectName('panelTitle')
        root.addWidget(title)

        controls = QHBoxLayout()
        controls.addWidget(QLabel('Динамика:'))
        self.metric_combo = QComboBox()
        self.metric_combo.addItems(['amount', 'quantity'])
        self.metric_combo.currentTextChanged.connect(self.refresh)
        controls.addWidget(self.metric_combo)
        controls.addStretch(1)
        root.addLayout(controls)

        visibility_row = QHBoxLayout()
        visibility_row.addWidget(QLabel('Плитки:'))
        self.tile_toggles: dict[str, QCheckBox] = {}

        self.tiles = QListWidget()
        self.tiles.setDragDropMode(QListWidget.InternalMove)
        self.tiles.setFlow(QListWidget.LeftToRight)
        self.tiles.setWrapping(True)
        self.tiles.setResizeMode(QListWidget.Adjust)
        self.tiles.setSpacing(10)

        self._tile_widgets = {}
        self._tile_items: dict[str, QListWidgetItem] = {}
        for key, title_text, size in [
            ('efficiency', 'Эффективность сети', QSize(460, 220)),
            ('status', 'Состояние сети', QSize(460, 220)),
            ('summary', 'Сводка', QSize(460, 220)),
            ('sales', 'Динамика продаж за последние 10 дней', QSize(920, 390)),
            ('news', 'Новости', QSize(460, 390)),
        ]:
            item = QListWidgetItem()
            item.setSizeHint(size)
            card = self._make_card(title_text)
            self.tiles.addItem(item)
            self.tiles.setItemWidget(item, card)
            self._tile_widgets[key] = card
            self._tile_items[key] = item

            toggle = QCheckBox(title_text)
            toggle.setChecked(True)
            toggle.toggled.connect(lambda checked, name=key: self._toggle_tile(name, checked))
            self.tile_toggles[key] = toggle
            visibility_row.addWidget(toggle)

        visibility_row.addStretch(1)
        root.addLayout(visibility_row)
        root.addWidget(self.tiles)

        self.refresh()

    def _toggle_tile(self, key: str, visible: bool):
        item = self._tile_items[key]
        item.setHidden(not visible)

    def _make_card(self, title: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName('panelCard')
        layout = QVBoxLayout(frame)
        title_lbl = QLabel(title)
        title_lbl.setObjectName('cardTitle')
        layout.addWidget(title_lbl)
        return frame

    def _clear_card(self, frame: QFrame):
        lay = frame.layout()
        while lay.count() > 1:
            item = lay.takeAt(1)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def refresh(self):
        try:
            eff = network_efficiency()
            status = network_status_breakdown()
            summary = summary_cards()
            sales = sales_last_10_days(self.metric_combo.currentText())
            news = franchise_news(10)
        except Exception as exc:
            for frame in self._tile_widgets.values():
                self._clear_card(frame)
                frame.layout().addWidget(QLabel(f'Ошибка данных: {exc}'))
            return

        self._render_efficiency(eff)
        self._render_status(status)
        self._render_summary(summary)
        self._render_sales(sales)
        self._render_news(news)

    def _render_efficiency(self, eff: float):
        card = self._tile_widgets['efficiency']
        self._clear_card(card)
        lbl = QLabel(f'Работающих автоматов: {eff:.2f}%')
        lbl.setObjectName('cardValueLabel')
        card.layout().addWidget(lbl)

    def _render_status(self, status: dict):
        card = self._tile_widgets['status']
        self._clear_card(card)
        series = QPieSeries()
        for k, v in status.items():
            series.append(k, v)
        chart = QChart()
        chart.addSeries(series)
        chart.legend().setVisible(False)
        chart.setBackgroundVisible(False)
        chart.setPlotAreaBackgroundVisible(False)
        card.layout().addWidget(QChartView(chart))

    def _render_summary(self, summary: dict):
        card = self._tile_widgets['summary']
        self._clear_card(card)
        grid = QGridLayout()
        pairs = [
            ('Денег в ТА', f"{summary['cash_total']:.2f}"),
            ('Продажи', f"{summary['sales_total']:.2f}"),
            ('Обслуживания', str(summary['maintenance_count'])),
        ]
        for i, (name, val) in enumerate(pairs):
            grid.addWidget(QLabel(name), i, 0)
            grid.addWidget(QLabel(val), i, 1)
        holder = QWidget()
        holder.setLayout(grid)
        card.layout().addWidget(holder)

    def _render_sales(self, sales: list[tuple[str, float]]):
        card = self._tile_widgets['sales']
        self._clear_card(card)

        bars = QBarSet('Динамика')
        days = []
        for day, value in sales:
            days.append(day[5:])
            bars.append(value)
        series = QBarSeries()
        series.append(bars)

        chart = QChart()
        chart.addSeries(series)
        chart.legend().setVisible(False)
        chart.setBackgroundVisible(False)

        ax_x = QBarCategoryAxis()
        ax_x.append(days)
        chart.addAxis(ax_x, Qt.AlignBottom)
        series.attachAxis(ax_x)

        ax_y = QValueAxis()
        chart.addAxis(ax_y, Qt.AlignLeft)
        series.attachAxis(ax_y)
        card.layout().addWidget(QChartView(chart))

    def _render_news(self, news: list[dict]):
        card = self._tile_widgets['news']
        self._clear_card(card)
        for item in news[:8]:
            card.layout().addWidget(QLabel(f"{item['created_at']:%d.%m.%y}  {item['title']}"))
