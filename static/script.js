// @ts-check

/** @ts-ignore */
const _Vue = Vue

/** @ts-ignore */
const _google = google

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

/**
 * Определение явной типизации
 * @param {any} myThis
 * @param {any} myLocalStorage
 * @returns {{_this: MyThis, _localStorage: MyLocaleStorage}}
 */
function typing(myThis, myLocalStorage) {
  /** @ts-ignore @type {MyThis} */
  const _this = myThis
  /** @ts-ignore @type {MyLocaleStorage} */
  const _localStorage = myLocalStorage
  return { _this, _localStorage }
}

new _Vue({
  el: "#app",
  /** @type {MyThis} */
  data: {
    dual_x_div_style: { width: "100%" }, // Стиль графика
    path: localStorage.path ? localStorage.path : "",
    size: localStorage.size ? localStorage.size : "",
    changes: [],
    statistics: [],
    commit: 0,
    line: 0,
    lineChanges: 0,
  },
  mounted() {},
  methods: {
    /**
     * Запись в локальное хранилище браузера
     * @returns {void}
     */
    inputMy() {
      const { _this, _localStorage } = typing(this, localStorage)
      _localStorage.path = _this.path
    },
    /**
     * Запрос данных с сервера
     * @returns {void}
     */
    update() {
      const { _this, _localStorage } = typing(this, localStorage)

      _localStorage.size = _this.size
      /** Запрос к серверу */
      const requestOptions = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ value: _this.path, size: _this.size }),
      }
      fetch("http://127.0.0.1:5000/post", requestOptions)
        .then((response) => response.json())
        .then((data) => {
          /** @type {MyResponse} */
          const _data = data

          _this.changes = _data.changes
          _this.statistics = _data.statistics
          _this.commit = _data.commit
          _this.line = _data.line
          _this.lineChanges = _data.lineChanges
        })
    },
  },
  watch: {
    /**
     * Отрисовка первого графика
     * @param {MyThis["changes"]} newChanges
     * @param {MyThis["changes"]} oldChanges
     * @returns {void}
     */
    changes(newChanges, oldChanges) {
      _google.charts.load("current", { packages: ["corechart"] })
      _google.charts.setOnLoadCallback(drawChart)

      function drawChart() {
        var data = _google.visualization.arrayToDataTable(newChanges)

        var options = {
          title: "Интенсивность работ",
          hAxis: { title: "Дни", titleTextStyle: { color: "#333" } },
          vAxis: { minValue: 0 },
        }

        var chart = new _google.visualization.AreaChart(
          document.getElementById("chart_div")
        )
        chart.draw(data, options)
      }
    },
    /**
     * Отрисовка второго графика
     * @param {MyThis["statistics"]} newStatistics
     * @param {MyThis["statistics"]} oldStatistics
     * @returns {void}
     */
    statistics(newStatistics, oldStatistics) {
      /* style */
      this.dual_x_div_style = {
        width: "70%",
        height: this.statistics.length * 20 + 180 + "px",
      }

      _google.charts.load("current", { packages: ["bar"] })
      _google.charts.setOnLoadCallback(drawStuff)

      function drawStuff() {
        var data = new _google.visualization.arrayToDataTable(newStatistics)

        var options = {
          // width: 800,
          chart: {
            title: "Объем работ",
            subtitle: "Количество коммитов и строк по файлам",
          },
          bars: "horizontal", // Required for Material Bar Charts.
          series: {
            0: { axis: "distance" }, // Bind series 0 to an axis named 'distance'.
            1: { axis: "brightness" }, // Bind series 1 to an axis named 'brightness'.
          },
          axes: {
            x: {
              distance: { label: "Коммиты" }, // Bottom x-axis.
              brightness: { side: "top", label: "Строки" }, // Top x-axis.
            },
          },
        }

        var chart = new _google.charts.Bar(
          document.getElementById("dual_x_div")
        )
        chart.draw(data, options)
      }
    },
  },
})
