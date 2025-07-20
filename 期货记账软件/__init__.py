import sys
import csv
from datetime import datetime, date
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QTabWidget, QMessageBox, QFileDialog, QHeaderView,
    QCalendarWidget, QGroupBox, QGridLayout, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor, QFont, QBrush

class CapitalManager:
    def __init__(self):
        self.balance = 0.0
        self.margin = 0.0
        self.transactions = []
    
    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            self.transactions.append(('入金', amount, datetime.now().strftime("%Y-%m-%d %H:%M")))
            return True
        return False
    
    def withdraw(self, amount):
        if 0 < amount <= self.balance:
            self.balance -= amount
            self.transactions.append(('出金', -amount, datetime.now().strftime("%Y-%m-%d %H:%M")))
            return True
        return False
    
    def set_margin(self, amount):
        if amount <= self.balance:
            self.margin = amount
            # 计算保证金占用比例
            ratio = (self.margin / self.balance) * 100 if self.balance > 0 else 0
            # 检查风险
            if self.balance > 0 and ratio >= 80:
                return True, f"请注意风险：保证金占用{ratio:.1f}%！"
            return True, ""
        return False, "保证金金额不能超过总资金"
    
    def available_balance(self):
        return self.balance - self.margin
    
    def margin_ratio(self):
        if self.balance <= 0:
            return 0
        return (self.margin / self.balance) * 100

class TradeRecorder:
    def __init__(self):
        self.trades = []
    
    def add_trade(self, trade_data):
        self.trades.append(trade_data)
    
    def calculate_daily_profit(self, date_str=None):
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
        total_profit = 0.0
        for trade in self.trades:
            if trade['date'] == date_str:
                total_profit += trade['profit']
        return total_profit
    
    def get_daily_profits(self):
        daily_profits = {}
        for trade in self.trades:
            date_str = trade['date']
            if date_str not in daily_profits:
                daily_profits[date_str] = 0.0
            daily_profits[date_str] += trade['profit']
        return daily_profits

class FuturesAccountingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.capital_manager = CapitalManager()
        self.trade_recorder = TradeRecorder()
        self.init_ui()
        self.setWindowTitle("期货交易记账软件")
        self.resize(1400, 900)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 12px;
            }
            QPushButton {
                padding: 5px 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            QTableWidget {
                background-color: white;
                gridline-color: #d0d0d0;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 4px;
                border: 1px solid #d0d0d0;
            }
            QGroupBox {
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
    
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # 创建标签页
        tabs = QTabWidget()
        self.trade_tab = self.create_trade_tab()
        self.capital_tab = self.create_capital_tab()
        self.history_tab = self.create_history_tab()
        
        tabs.addTab(self.trade_tab, "📝 交易记录")
        tabs.addTab(self.capital_tab, "💰 资金管理")
        tabs.addTab(self.history_tab, "📊 历史记录")
        
        main_layout.addWidget(tabs)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # 状态栏
        self.statusBar().showMessage("就绪")
    
    def create_trade_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 交易输入区域
        input_group = QGroupBox("交易输入")
        input_layout = QVBoxLayout(input_group)
        
        # 名称和价格
        grid_layout = QHBoxLayout()
        left_form = QVBoxLayout()
        right_form = QVBoxLayout()
        
        # 左边表单
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("例如: 沪铜2308")
        self.open_price_input = QLineEdit()
        self.open_price_input.setPlaceholderText("开仓价格")
        self.close_price_input = QLineEdit()
        self.close_price_input.setPlaceholderText("平仓价格")
        
        left_form.addWidget(QLabel("期货名称:"))
        left_form.addWidget(self.name_input)
        left_form.addWidget(QLabel("开仓价格:"))
        left_form.addWidget(self.open_price_input)
        left_form.addWidget(QLabel("平仓价格:"))
        left_form.addWidget(self.close_price_input)
        
        # 右边表单
        # 盈利计算选项
        profit_layout = QHBoxLayout()
        self.profit_combo = QComboBox()
        self.profit_combo.addItems(["5元/点", "10元/点", "20元/点", "自定义"])
        self.custom_profit_input = QLineEdit()
        self.custom_profit_input.setPlaceholderText("输入每点盈利")
        self.custom_profit_input.setEnabled(False)
        
        self.profit_combo.currentTextChanged.connect(lambda: self.custom_profit_input.setEnabled(
            self.profit_combo.currentText() == "自定义"))
        
        profit_layout.addWidget(self.profit_combo)
        profit_layout.addWidget(self.custom_profit_input)
        
        # 手续费
        fee_layout = QHBoxLayout()
        self.open_fee_input = QLineEdit()
        self.open_fee_input.setPlaceholderText("开仓手续费 (元)")
        self.close_fee_input = QLineEdit()
        self.close_fee_input.setPlaceholderText("平仓手续费 (元)")
        fee_layout.addWidget(self.open_fee_input)
        fee_layout.addWidget(self.close_fee_input)
        
        # 日期选择
        self.trade_date_input = QLineEdit()
        self.trade_date_input.setText(datetime.now().strftime("%Y-%m-%d"))
        self.trade_date_input.setPlaceholderText("交易日期 (YYYY-MM-DD)")
        
        right_form.addWidget(QLabel("每点盈利:"))
        right_form.addLayout(profit_layout)
        right_form.addWidget(QLabel("手续费:"))
        right_form.addLayout(fee_layout)
        right_form.addWidget(QLabel("交易日期:"))
        right_form.addWidget(self.trade_date_input)
        
        grid_layout.addLayout(left_form)
        grid_layout.addLayout(right_form)
        input_layout.addLayout(grid_layout)
        
        # 添加按钮
        button_layout = QHBoxLayout()
        add_button = QPushButton("➕ 添加交易")
        add_button.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14px;")
        add_button.clicked.connect(self.add_trade)
        button_layout.addWidget(add_button)
        input_layout.addLayout(button_layout)
        
        # 当日盈亏显示
        daily_profit_group = QGroupBox("当日盈亏")
        daily_layout = QHBoxLayout(daily_profit_group)
        self.daily_profit_label = QLabel("0.00 元")
        self.daily_profit_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        daily_layout.addWidget(self.daily_profit_label)
        
        # 交易记录表格
        table_group = QGroupBox("交易记录")
        table_layout = QVBoxLayout(table_group)
        self.trade_table = QTableWidget()
        self.trade_table.setColumnCount(8)
        self.trade_table.setHorizontalHeaderLabels(["日期", "名称", "开仓价", "平仓价", "每点盈利", "开仓费", "平仓费", "盈亏"])
        self.trade_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.trade_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table_layout.addWidget(self.trade_table)
        
        layout.addWidget(input_group)
        layout.addWidget(daily_profit_group)
        layout.addWidget(table_group, 1)
        tab.setLayout(layout)
        return tab
    
    def create_capital_tab(self):
        tab = QWidget()
        layout = QGridLayout()
        layout.setSpacing(15)
        
        # 资金信息显示
        capital_info_group = QGroupBox("资金概览")
        info_layout = QVBoxLayout(capital_info_group)
        
        self.balance_label = QLabel("总资金: 0.00 元")
        self.balance_label.setFont(QFont("Arial", 12))
        self.margin_label = QLabel("保证金占用: 0.00 元")
        self.margin_label.setFont(QFont("Arial", 12))
        self.ratio_label = QLabel("保证金比例: 0.0%")
        self.ratio_label.setFont(QFont("Arial", 12))
        self.available_label = QLabel("可用资金: 0.00 元")
        self.available_label.setFont(QFont("Arial", 12))
        self.risk_label = QLabel("")
        self.risk_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
        
        info_layout.addWidget(self.balance_label)
        info_layout.addWidget(self.margin_label)
        info_layout.addWidget(self.ratio_label)
        info_layout.addWidget(self.available_label)
        info_layout.addWidget(self.risk_label)
        
        # 资金操作
        capital_operation_group = QGroupBox("资金操作")
        capital_layout = QVBoxLayout(capital_operation_group)
        
        # 入金出金
        deposit_withdraw_group = QWidget()
        dw_layout = QHBoxLayout(deposit_withdraw_group)
        
        self.capital_input = QLineEdit()
        self.capital_input.setPlaceholderText("金额 (元)")
        deposit_button = QPushButton("💵 入金")
        deposit_button.setStyleSheet("background-color: #2196F3; color: white; font-size: 14px;")
        deposit_button.clicked.connect(self.deposit)
        withdraw_button = QPushButton("💸 出金")
        withdraw_button.setStyleSheet("background-color: #FF9800; color: white; font-size: 14px;")
        withdraw_button.clicked.connect(self.withdraw)
        
        dw_layout.addWidget(QLabel("金额:"))
        dw_layout.addWidget(self.capital_input)
        dw_layout.addWidget(deposit_button)
        dw_layout.addWidget(withdraw_button)
        
        # 保证金设置
        margin_group = QWidget()
        margin_layout = QHBoxLayout(margin_group)
        
        self.margin_input = QLineEdit()
        self.margin_input.setPlaceholderText("保证金金额 (元)")
        set_margin_button = QPushButton("🛡️ 设置保证金")
        set_margin_button.setStyleSheet("background-color: #9C27B0; color: white; font-size: 14px;")
        set_margin_button.clicked.connect(self.set_margin)
        
        margin_layout.addWidget(QLabel("保证金:"))
        margin_layout.addWidget(self.margin_input)
        margin_layout.addWidget(set_margin_button)
        
        capital_layout.addWidget(QLabel("资金操作:"))
        capital_layout.addWidget(deposit_withdraw_group)
        capital_layout.addWidget(QLabel("保证金设置:"))
        capital_layout.addWidget(margin_group)
        
        # 资金变动表格
        capital_table_group = QGroupBox("资金变动记录")
        capital_table_layout = QVBoxLayout(capital_table_group)
        self.capital_table = QTableWidget()
        self.capital_table.setColumnCount(3)
        self.capital_table.setHorizontalHeaderLabels(["类型", "金额", "时间"])
        self.capital_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.capital_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        capital_table_layout.addWidget(self.capital_table)
        
        # 日历和每日盈利
        calendar_group = QGroupBox("每日盈利日历")
        calendar_layout = QVBoxLayout(calendar_group)
        
        # 创建日历控件
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setStyleSheet("""
            QCalendarWidget QAbstractItemView:enabled {
                selection-background-color: #4CAF50;
                selection-color: white;
            }
        """)
        self.calendar.selectionChanged.connect(self.on_calendar_date_selected)
        
        # 显示选中日期的盈利
        self.calendar_profit_label = QLabel("请选择日期查看当日盈亏")
        self.calendar_profit_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.calendar_profit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.calendar_profit_label.setStyleSheet("background-color: #e0f7fa; padding: 10px; border-radius: 5px;")
        
        calendar_layout.addWidget(self.calendar)
        calendar_layout.addWidget(self.calendar_profit_label)
        
        # 布局安排
        layout.addWidget(capital_info_group, 0, 0)
        layout.addWidget(capital_operation_group, 1, 0)
        layout.addWidget(capital_table_group, 2, 0)
        layout.addWidget(calendar_group, 0, 1, 3, 1)  # 跨3行
        
        # 设置列宽比例
        layout.setColumnStretch(0, 2)
        layout.setColumnStretch(1, 1)
        
        tab.setLayout(layout)
        return tab
    
    def create_history_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # 操作按钮
        button_group = QGroupBox("数据操作")
        button_layout = QHBoxLayout(button_group)
        
        load_button = QPushButton("📂 加载数据")
        load_button.setStyleSheet("background-color: #607D8B; color: white; font-size: 14px;")
        load_button.clicked.connect(self.load_data)
        save_button = QPushButton("💾 保存数据")
        save_button.setStyleSheet("background-color: #009688; color: white; font-size: 14px;")
        save_button.clicked.connect(self.save_data)
        
        button_layout.addWidget(load_button)
        button_layout.addWidget(save_button)
        
        # 历史记录表格
        history_group = QGroupBox("历史交易记录")
        history_layout = QVBoxLayout(history_group)
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels(["日期", "名称", "开仓价", "平仓价", "每点盈利", "开仓费", "平仓费", "盈亏"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        history_layout.addWidget(self.history_table)
        
        layout.addWidget(button_group)
        layout.addWidget(history_group, 1)
        tab.setLayout(layout)
        return tab
    
    def deposit(self):
        amount_text = self.capital_input.text()
        if not amount_text:
            QMessageBox.warning(self, "输入错误", "请输入入金金额")
            return
        
        try:
            amount = float(amount_text)
            if self.capital_manager.deposit(amount):
                self.update_capital_display()
                self.capital_input.clear()
                self.statusBar().showMessage(f"成功入金 {amount:.2f} 元", 5000)
            else:
                QMessageBox.warning(self, "操作失败", "入金金额必须大于0")
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的数字")
    
    def withdraw(self):
        amount_text = self.capital_input.text()
        if not amount_text:
            QMessageBox.warning(self, "输入错误", "请输入出金金额")
            return
        
        try:
            amount = float(amount_text)
            if self.capital_manager.withdraw(amount):
                self.update_capital_display()
                self.capital_input.clear()
                self.statusBar().showMessage(f"成功出金 {amount:.2f} 元", 5000)
            else:
                QMessageBox.warning(self, "操作失败", "出金金额不能大于可用资金")
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的数字")
    
    def add_trade(self):
        # 获取输入值
        name = self.name_input.text().strip()
        open_price = self.open_price_input.text().strip()
        close_price = self.close_price_input.text().strip()
        open_fee = self.open_fee_input.text().strip() or "0"
        close_fee = self.close_fee_input.text().strip() or "0"
        trade_date = self.trade_date_input.text().strip()
        
        # 验证输入
        if not all([name, open_price, close_price]):
            QMessageBox.warning(self, "输入错误", "请填写期货名称和价格")
            return
        
        try:
            open_price = float(open_price)
            close_price = float(close_price)
            open_fee = float(open_fee)
            close_fee = float(close_fee)
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的数字")
            return
        
        # 验证日期格式
        if trade_date:
            try:
                datetime.strptime(trade_date, "%Y-%m-%d")
            except ValueError:
                QMessageBox.warning(self, "日期格式错误", "请使用 YYYY-MM-DD 格式")
                return
        else:
            trade_date = datetime.now().strftime("%Y-%m-%d")
        
        # 获取每点盈利值
        profit_per_point = 0
        if self.profit_combo.currentText() == "自定义" and self.custom_profit_input.text().strip():
            try:
                profit_per_point = float(self.custom_profit_input.text().strip())
            except ValueError:
                QMessageBox.warning(self, "输入错误", "请输入有效的自定义盈利值")
                return
        else:
            # 从选项中提取数字
            text = self.profit_combo.currentText()
            if text == "5元/点":
                profit_per_point = 5
            elif text == "10元/点":
                profit_per_point = 10
            elif text == "20元/点":
                profit_per_point = 20
            else:
                QMessageBox.warning(self, "输入错误", "请选择或输入有效的每点盈利值")
                return
        
        # 计算盈亏
        price_diff = close_price - open_price
        profit = price_diff * profit_per_point - open_fee - close_fee
        
        # 创建交易记录
        trade = {
            'date': trade_date,
            'name': name,
            'open_price': open_price,
            'close_price': close_price,
            'profit_per_point': profit_per_point,
            'open_fee': open_fee,
            'close_fee': close_fee,
            'profit': profit
        }
        
        self.trade_recorder.add_trade(trade)
        self.update_trade_table()
        self.update_daily_profit()
        
        # 清空输入字段
        self.name_input.clear()
        self.open_price_input.clear()
        self.close_price_input.clear()
        self.open_fee_input.clear()
        self.close_fee_input.clear()
        self.custom_profit_input.clear()
        self.trade_date_input.setText(datetime.now().strftime("%Y-%m-%d"))
        
        self.statusBar().showMessage(f"成功添加交易: {name}, 盈亏: {profit:.2f} 元", 5000)
    
    def set_margin(self):
        margin_text = self.margin_input.text().strip()
        if not margin_text:
            QMessageBox.warning(self, "输入错误", "请输入保证金金额")
            return
        
        try:
            margin = float(margin_text)
            success, message = self.capital_manager.set_margin(margin)
            if success:
                self.update_capital_display()
                if message:
                    self.risk_label.setText(message)
                    self.statusBar().showMessage(message, 5000)
                self.margin_input.clear()
            else:
                QMessageBox.warning(self, "操作失败", message)
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请输入有效的保证金金额")
    
    def update_trade_table(self):
        self.trade_table.setRowCount(len(self.trade_recorder.trades))
        for row, trade in enumerate(self.trade_recorder.trades):
            self.trade_table.setItem(row, 0, QTableWidgetItem(trade['date']))
            self.trade_table.setItem(row, 1, QTableWidgetItem(trade['name']))
            self.trade_table.setItem(row, 2, QTableWidgetItem(f"{trade['open_price']:.2f}"))
            self.trade_table.setItem(row, 3, QTableWidgetItem(f"{trade['close_price']:.2f}"))
            self.trade_table.setItem(row, 4, QTableWidgetItem(f"{trade['profit_per_point']:.2f}"))
            self.trade_table.setItem(row, 5, QTableWidgetItem(f"{trade['open_fee']:.2f}"))
            self.trade_table.setItem(row, 6, QTableWidgetItem(f"{trade['close_fee']:.2f}"))
            
            profit_item = QTableWidgetItem(f"{trade['profit']:.2f}")
            if trade['profit'] >= 0:
                profit_item.setForeground(QColor(Qt.GlobalColor.darkGreen))
            else:
                profit_item.setForeground(QColor(Qt.GlobalColor.red))
            self.trade_table.setItem(row, 7, profit_item)
    
    def update_daily_profit(self):
        if not self.trade_recorder.trades:
            self.daily_profit_label.setText("0.00 元")
            return
            
        # 获取当前日期或最后交易日期
        last_date = self.trade_recorder.trades[-1]['date']
        daily_profit = self.trade_recorder.calculate_daily_profit(last_date)
        
        self.daily_profit_label.setText(f"{daily_profit:.2f} 元")
        if daily_profit >= 0:
            self.daily_profit_label.setStyleSheet("color: darkgreen; font-size: 16px; font-weight: bold;")
        else:
            self.daily_profit_label.setStyleSheet("color: red; font-size: 16px; font-weight: bold;")
    
    def update_capital_display(self):
        self.balance_label.setText(f"总资金: {self.capital_manager.balance:.2f} 元")
        self.margin_label.setText(f"保证金占用: {self.capital_manager.margin:.2f} 元")
        self.ratio_label.setText(f"保证金比例: {self.capital_manager.margin_ratio():.1f}%")
        self.available_label.setText(f"可用资金: {self.capital_manager.available_balance():.2f} 元")
        
        # 检查风险
        ratio = self.capital_manager.margin_ratio()
        if ratio >= 80:
            self.risk_label.setText(f"请注意风险：保证金占用{ratio:.1f}%！")
            self.risk_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
        else:
            self.risk_label.setText("")
        
        # 更新资金表格
        self.capital_table.setRowCount(len(self.capital_manager.transactions))
        for row, (trans_type, amount, time) in enumerate(self.capital_manager.transactions):
            self.capital_table.setItem(row, 0, QTableWidgetItem(trans_type))
            
            amount_item = QTableWidgetItem(f"{amount:.2f}")
            if amount >= 0:
                amount_item.setForeground(QColor(Qt.GlobalColor.darkGreen))
            else:
                amount_item.setForeground(QColor(Qt.GlobalColor.red))
            self.capital_table.setItem(row, 1, amount_item)
            
            self.capital_table.setItem(row, 2, QTableWidgetItem(time))
    
    def save_data(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存数据", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # 确保文件扩展名正确
            if not file_path.lower().endswith('.csv'):
                file_path += '.csv'
            
            # 保存交易记录
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["type", "data"])
                
                # 保存资金记录
                for trans in self.capital_manager.transactions:
                    writer.writerow(["capital", f"{trans[0]},{trans[1]},{trans[2]}"])
                
                # 保存交易记录
                for trade in self.trade_recorder.trades:
                    writer.writerow(["trade", (
                        f"{trade['date']},{trade['name']},{trade['open_price']},"
                        f"{trade['close_price']},{trade['profit_per_point']},"
                        f"{trade['open_fee']},{trade['close_fee']},{trade['profit']}"
                    )])
            
            self.statusBar().showMessage(f"数据已成功保存到: {file_path}", 7000)
            QMessageBox.information(self, "保存成功", f"数据已成功保存到:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存数据时出错: {str(e)}")
    
    def load_data(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载数据", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            self.capital_manager = CapitalManager()
            self.trade_recorder = TradeRecorder()
            
            with open(file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # 跳过标题行
                
                for row in reader:
                    if row[0] == "capital":
                        trans_data = row[1].split(',')
                        trans_type = trans_data[0]
                        amount = float(trans_data[1])
                        time = trans_data[2]
                        self.capital_manager.transactions.append((trans_type, amount, time))
                        
                        # 更新资金余额
                        if trans_type == "入金":
                            self.capital_manager.balance += amount
                        elif trans_type == "出金":
                            self.capital_manager.balance -= amount
                    
                    elif row[0] == "trade":
                        trade_data = row[1].split(',')
                        trade = {
                            'date': trade_data[0],
                            'name': trade_data[1],
                            'open_price': float(trade_data[2]),
                            'close_price': float(trade_data[3]),
                            'profit_per_point': float(trade_data[4]),
                            'open_fee': float(trade_data[5]),
                            'close_fee': float(trade_data[6]),
                            'profit': float(trade_data[7])
                        }
                        self.trade_recorder.trades.append(trade)
            
            # 更新UI
            self.update_trade_table()
            self.update_daily_profit()
            self.update_capital_display()
            self.update_history_table()
            
            # 更新日历
            self.update_calendar()
            
            self.statusBar().showMessage(f"成功从 {file_path} 加载数据", 7000)
            QMessageBox.information(self, "加载成功", f"已成功加载 {len(self.trade_recorder.trades)} 条交易记录")
        except Exception as e:
            QMessageBox.critical(self, "加载失败", f"加载数据时出错: {str(e)}")
    
    def update_history_table(self):
        self.history_table.setRowCount(len(self.trade_recorder.trades))
        for row, trade in enumerate(self.trade_recorder.trades):
            self.history_table.setItem(row, 0, QTableWidgetItem(trade['date']))
            self.history_table.setItem(row, 1, QTableWidgetItem(trade['name']))
            self.history_table.setItem(row, 2, QTableWidgetItem(f"{trade['open_price']:.2f}"))
            self.history_table.setItem(row, 3, QTableWidgetItem(f"{trade['close_price']:.2f}"))
            self.history_table.setItem(row, 4, QTableWidgetItem(f"{trade['profit_per_point']:.2f}"))
            self.history_table.setItem(row, 5, QTableWidgetItem(f"{trade['open_fee']:.2f}"))
            self.history_table.setItem(row, 6, QTableWidgetItem(f"{trade['close_fee']:.2f}"))
            
            profit_item = QTableWidgetItem(f"{trade['profit']:.2f}")
            if trade['profit'] >= 0:
                profit_item.setForeground(QColor(Qt.GlobalColor.darkGreen))
            else:
                profit_item.setForeground(QColor(Qt.GlobalColor.red))
            self.history_table.setItem(row, 7, profit_item)
    
    def update_calendar(self):
        """更新日历中每日盈利的显示"""
        daily_profits = self.trade_recorder.get_daily_profits()
        
        # 清除所有格式
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        # 为有交易记录的日期设置格式
        for date_str, profit in daily_profits.items():
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                qdate = QDate(date_obj.year, date_obj.month, date_obj.day)
                
                # 创建文本格式
                fmt = QTextCharFormat()
                if profit >= 0:
                    fmt.setBackground(QBrush(QColor(200, 255, 200)))  # 浅绿色
                    fmt.setForeground(QBrush(QColor(0, 100, 0)))       # 深绿色
                else:
                    fmt.setBackground(QBrush(QColor(255, 200, 200)))  # 浅红色
                    fmt.setForeground(QBrush(QColor(139, 0, 0)))       # 深红色
                
                # 应用格式
                self.calendar.setDateTextFormat(qdate, fmt)
            except ValueError:
                continue
    
    def on_calendar_date_selected(self):
        """当选择日历日期时显示该日的盈利"""
        selected_date = self.calendar.selectedDate()
        date_str = selected_date.toString("yyyy-MM-dd")
        daily_profit = self.trade_recorder.calculate_daily_profit(date_str)
        
        if daily_profit == 0:
            self.calendar_profit_label.setText(f"{date_str} 没有交易记录")
            self.calendar_profit_label.setStyleSheet("background-color: #e0e0e0; padding: 10px; border-radius: 5px;")
        else:
            if daily_profit >= 0:
                color = "#4CAF50"
                text_color = "white"
                result = "盈利"
            else:
                color = "#F44336"
                text_color = "white"
                result = "亏损"
            
            self.calendar_profit_label.setText(
                f"{date_str} {result} {abs(daily_profit):.2f} 元"
            )
            self.calendar_profit_label.setStyleSheet(
                f"background-color: {color}; color: {text_color}; "
                "padding: 10px; border-radius: 5px; font-weight: bold;"
            )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # 设置应用样式
    app.setStyle("Fusion")
    
    # 设置全局字体
    font = QFont("Microsoft YaHei UI", 10)
    app.setFont(font)
    
    window = FuturesAccountingApp()
    window.show()
    sys.exit(app.exec())