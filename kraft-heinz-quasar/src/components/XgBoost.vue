<template>
  <q-inner-loading
    :showing="data === null"
    label="Please wait..."
    color="primary"
    label-style="font-size: 1.1em"
    label-class="text-primary"
  />

  <div
    class="q-gutter-y-md column items-start"
    v-if="data !== null"
  >
    <q-select
      filled
      v-model="selectedLine"
      label="Line"
      :options="lines"
      @filter="filterFn"
      style="width: 100%"
    >
      <template v-slot:no-option>
        <q-item>
          <q-item-section class="text-grey">
            No results
          </q-item-section>
        </q-item>
      </template>
    </q-select>
    <q-date
      v-model="model"
      range
      :options="options"
      :navigation-max-year-month="navigationMaxYearMonth"
      :navigation-min-year-month="navigationMinYearMonth"
    />
  </div>

  <div
    v-if="data !== null"
    ref="chartEl"
    style="width: 60%; height: 500px"
  />
</template>

<script lang="ts">
import { api } from 'src/boot/axios';
import { defineComponent, computed, watch, Ref, ref, shallowRef } from 'vue';
import * as echarts from 'echarts';
import { cloneDeep, uniq } from 'lodash';

interface XGBoostDTO {
  Actual: number[];
  Dates: string[];
  'Next date': string;
  'Next prediction': string;
  Predicted: number[];
}

const lineOptions = ['1', '3', '4', '5', '6', '7', '8', '11', '13', '14'];

export default defineComponent({
  props: {},
  setup() {
    const data = ref(null as XGBoostDTO | null);
    const lines = ref(lineOptions);
    const selectedLine = ref(lineOptions[0]);

    function fetch() {
      void api.get(`cases_overfill/${selectedLine.value}`).then((res) => {
        console.log(res);
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        data.value = res.data;
      });
    }

    fetch();

    watch(
      selectedLine,
      () => {
        fetch();
      },
      { immediate: true }
    );

    const model: Ref<typeof computedModel.value | null> = ref(null);

    const transformedData = computed(() => {
      if (data.value) {
        const copy = cloneDeep(data.value);
        const value = {
          ...copy,
          Dates: copy.Dates.map((date) => new Date(date)),
          'Next date': new Date(copy['Next date']) as Date | null,
          'Next prediction': copy['Next prediction'] as unknown as
            | number
            | null,
        };

        return value;
      } else {
        return {
          Dates: [],
          'Next date': null,
          'Next prediction': null,
          Actual: [],
          Predicted: [],
        };
      }
    });

    const filteredData = computed(() => {
      const value = cloneDeep(transformedData.value);
      if (model.value === null) return value;

      let firstDateInRangeIndex = -1;
      let lastDateInRangeIndex = -1;
      const from = new Date(model.value.from);
      const to = new Date(model.value.to);
      value.Dates.forEach((date, index) => {
        if (date >= from && date <= to) {
          if (firstDateInRangeIndex === -1) firstDateInRangeIndex = index;
        } else {
          if (firstDateInRangeIndex !== -1) lastDateInRangeIndex = index;
        }
      });

      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      value.Dates = value.Dates.slice(
        firstDateInRangeIndex,
        lastDateInRangeIndex
      ).map((date) => date.toLocaleString('en-US'));
      value.Actual = value.Actual.slice(
        firstDateInRangeIndex,
        lastDateInRangeIndex
      );
      value.Predicted = value.Predicted.slice(
        firstDateInRangeIndex,
        lastDateInRangeIndex
      );

      function sameDay(d1: Date, d2: Date) {
        return (
          d1.getFullYear() === d2.getFullYear() &&
          d1.getMonth() === d2.getMonth() &&
          d1.getDate() === d2.getDate()
        );
      }

      let isOneDayFromPredictedDate = false;
      if (value['Next date'] !== null)
        isOneDayFromPredictedDate = sameDay(value['Next date'], to);

      if (!isOneDayFromPredictedDate) {
        value['Next prediction'] = null;
        value['Next date'] = null;
      } else {
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        value['Next date'] = value['Next date']?.toLocaleString('en-US');
      }

      return value;
    });

    const optionsAsDates = computed(() => {
      const allOptions = transformedData.value.Dates.map((date) => {
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');

        return `${year}/${month}/${day}`;
      });

      const uniqueOptions = uniq(allOptions);
      return uniqueOptions;
    });

    const computedModel = computed(() => {
      const dateBeforeLastDate =
        optionsAsDates.value[optionsAsDates.value.length - 2];
      const lastDate = optionsAsDates.value[optionsAsDates.value.length - 1];

      const from = dateBeforeLastDate;
      const to = lastDate;

      return { from, to };
    });

    watch(
      computedModel,
      () => {
        model.value = cloneDeep(computedModel.value);
      },
      { immediate: true }
    );

    const optionsAsMonths = computed(() => {
      const allOptions = transformedData.value.Dates.map((date) => {
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');

        return `${year}/${month}`;
      });

      const uniqueOptions = uniq(allOptions);
      return uniqueOptions;
    });

    const navigationMinYearMonth = computed(() => {
      const firstDate = optionsAsMonths.value[0];

      return firstDate;
    });

    const navigationMaxYearMonth = computed(() => {
      const lastDate = optionsAsMonths.value[optionsAsMonths.value.length - 1];

      return lastDate;
    });

    const chart: Ref<echarts.ECharts | null> = shallowRef(null);
    const chartEl: Ref<HTMLElement | null> = ref(null);

    watch(
      [filteredData, chartEl],
      () => {
        const nextPredictionArray = Array(filteredData.value.Dates.length).fill(
          null
        );
        nextPredictionArray.push(filteredData.value['Next prediction']);

        const option = {
          title: {
            text: 'Rejected Cases Next 3 Hours',
          },
          tooltip: {
            trigger: 'item',
          },
          legend: {
            data: ['Actual', 'Predicted', 'Next prediction'],
          },
          grid: {
            left: '3%',
            right: '3%',
            bottom: '0%',
            containLabel: true,
          },
          toolbox: {
            feature: {
              saveAsImage: {},
            },
          },
          xAxis: {
            type: 'category',
            data: [
              ...filteredData.value.Dates,
              data.value
                ? new Date(data.value['Next date']).toLocaleString('en-US')
                : [],
            ],
            axisLabel: {
              formatter: function (value: Date) {
                const label = new Date(value).toLocaleString('en-US');
                return label;
              },
            },
          },
          yAxis: [
            {
              type: 'value',
            },
            {
              type: 'value',
            },
            {
              type: 'value',
            },
          ],
          series: [
            {
              name: 'Actual',
              type: 'line',
              data: filteredData.value.Actual,
            },
            {
              name: 'Predicted',
              type: 'line',
              data: filteredData.value.Predicted,
            },
            {
              name: 'Next prediction',
              type: 'scatter',
              data: nextPredictionArray,
            },
          ],
        };

        if (chart.value !== null && chart.value !== undefined) {
          chart.value.dispose();
        }

        if (chartEl.value !== null) {
          chart.value = echarts.init(chartEl.value);
          chart.value.setOption(option);
        }
      },
      { immediate: true, deep: true }
    );

    return {
      chartEl,
      model,
      options: optionsAsDates,
      navigationMinYearMonth,
      navigationMaxYearMonth,
      data,
      lines,
      selectedLine,
      filterFn(val: string, update: (arg0: () => void) => void) {
        update(() => {
          const needle = val.toLowerCase();
          lines.value = lineOptions.filter(
            (v) => v.toLowerCase().indexOf(needle) > -1
          );
        });
      },
    };
  },
});
</script>
