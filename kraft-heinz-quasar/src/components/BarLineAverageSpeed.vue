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
    v-if="data !==null"
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
      mask="DD-MM-YYYY"
    />
  </div>

  <div
    v-if="data !==null"
    ref="chartEl"
    style="width: 60%; height: 500px"
  />
</template>

<script lang="ts">
import { api } from 'src/boot/axios';
import { defineComponent, computed, watch, Ref, ref, shallowRef } from 'vue';
import * as echarts from 'echarts';
import { cloneDeep } from 'lodash';

interface BarLineAverageSpeedDTO {
  x_axis: number[];
  y_axis_amount_of_overfill_cases: number[];
  y_axis_cases_produced: number[];
  y_axis_overfill: number[];
  y_axis_time_spend: number[];
}

const lineOptions = ['1', '3', '4', '5', '6', '7', '8', '11', '13', '14'];

export default defineComponent({
  props: {},
  setup() {
    const data = ref(null as BarLineAverageSpeedDTO | null);

    const model = ref(null as typeof computedModel.value | null);
    const lines = ref(lineOptions);
    const selectedLine = ref(lineOptions[0]);

    const chart: Ref<echarts.ECharts | null> = shallowRef(null);
    const chartEl: Ref<HTMLElement | null> = ref(null);

    const producedCasesNormalized = computed(() => {
      const amountOfCasesProduced = data.value?.y_axis_cases_produced;
      if (amountOfCasesProduced === undefined) {
        return [];
      }
      const timeSpent = data.value?.y_axis_time_spend;
      if (timeSpent === undefined) {
        return amountOfCasesProduced;
      }

      return amountOfCasesProduced.map((value, index) => {
        return Math.round(value / timeSpent[index]);
      });
    });

    const overfillCasesNormalized = computed(() => {
      const amountOfOverfillCases = data.value?.y_axis_amount_of_overfill_cases;
      if (amountOfOverfillCases === undefined) {
        return [];
      }
      const timeSpent = data.value?.y_axis_time_spend;
      if (timeSpent === undefined) {
        return amountOfOverfillCases;
      }

      return amountOfOverfillCases.map((value, index) => {
        return Math.round(value / timeSpent[index]);
      });
    });

    const overfilledCasesDividedByProduced = computed(() => {
      return overfillCasesNormalized.value.map((overfilled, index) => {
        const produced = producedCasesNormalized.value[index];
        return ((overfilled / produced) * 100).toFixed(2);
      });
    });

    function fetch() {
      void api
        .get(
          `average_vs_overfill/${model.value?.from ?? ''}/${
            model.value?.to ?? ''
          }/${selectedLine.value}`
        )
        .then((res) => {
          // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
          data.value = res.data;
        });
    }

    watch(
      model,
      () => {
        fetch();
      },
      { deep: true }
    );

    watch(selectedLine, () => {
      fetch();
    });

    const computedModel = computed(() => {
      return {
        from: '08-04-2019',
        to: '08-09-2021',
      };
    });

    watch(
      computedModel,
      () => {
        model.value = cloneDeep(computedModel.value);
      },
      { immediate: true }
    );

    watch(
      [data, chartEl],
      () => {
        const option = {
          title: {
            text: 'Average Line Speed',
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'cross',
              crossStyle: {
                color: '#999',
              },
            },
          },
          toolbox: {
            feature: {
              dataView: { show: true, readOnly: false },
              magicType: { show: true, type: ['line', 'bar'] },
              restore: { show: true },
              saveAsImage: { show: true },
            },
          },
          legend: {
            data: [
              'Number of overfill cases',
              'Number of cases produced',
              // 'Overfill',
              'Time spent',
            ],
          },
          xAxis: [
            {
              type: 'category',
              data: data.value?.x_axis,
              axisPointer: {
                type: 'shadow',
              },
              name: 'Average speed',
              nameLocation: 'center',
              nameGap: '25',
            },
          ],
          yAxis: [
            {
              type: 'value',
              name: 'Number of cases produced',
            },
            {
              type: 'value',
              name: 'Time spent',
              axisLabel: {
                formatter: '{value} hours',
              },
            },
          ],
          series: [
            {
              name: 'Number of overfill cases',
              type: 'line',
              data: overfillCasesNormalized.value,
            },
            {
              name: 'Number of cases produced',
              type: 'line',
              data: producedCasesNormalized.value,
            },
            {
              name: 'Overfilled/Produced',
              type: 'line',
              data: overfilledCasesDividedByProduced.value,
              symbolSize: 0,
            },
            {
              name: 'Time spent',
              type: 'bar',
              data: data.value?.y_axis_time_spend,
              yAxisIndex: 1,
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
      data,
      model,
      chartEl,
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
