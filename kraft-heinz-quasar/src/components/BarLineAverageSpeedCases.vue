<template>
  <q-inner-loading
    :showing="isFetching"
    label="Please wait..."
    color="primary"
    label-style="font-size: 1.1em"
    label-class="text-primary"
  />
  <div
    class="q-gutter-y-md column items-start"
    v-if="!isFetching"
  >
    <q-btn-toggle
      v-model="isQuarterly"
      spread
      class="my-custom-toggle"
      style="width: 100%"
      no-caps
      rounded
      unelevated
      toggle-color="primary"
      color="white"
      text-color="primary"
      :options="[
          {label: 'Quarterly', value: true},
          {label: 'Hourly', value: false}
        ]"
    />
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
    v-if="!isFetching"
    ref="chartEl"
    style="width: 60%; height: 500px"
  />
</template>

<script lang="ts">
import { api } from 'src/boot/axios';
import { defineComponent, computed, watch, Ref, ref, shallowRef } from 'vue';
import * as echarts from 'echarts';
import { EChartOption } from 'echarts';
import { cloneDeep, isArray } from 'lodash';

interface BarLineAverageSpeedDTO {
  x_axis: number[];
  y_axis_number_of_rejected_cases: number[];
  y_axis_cases_produced: number[];
  y_axis_overfill: number[];
  y_axis_time_spend: number[];
}

const lineOptions = ['1', '3', '4', '5', '6', '7', '8', '11', '13', '14'];

export default defineComponent({
  props: {},
  setup() {
    const data = ref(null as BarLineAverageSpeedDTO | null);
    const isFetching = ref(true);

    const model = ref(null as typeof computedModel.value | null);
    const lines = ref(lineOptions);
    const selectedLine = ref(lineOptions[0]);

    const isQuarterly = ref(true);

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

    const rejectedCasesNormalized = computed(() => {
      const numberOfRejectedCases = data.value?.y_axis_number_of_rejected_cases;
      if (numberOfRejectedCases === undefined) {
        return [];
      }
      const timeSpent = data.value?.y_axis_time_spend;
      if (timeSpent === undefined) {
        return numberOfRejectedCases;
      }

      return numberOfRejectedCases.map((value, index) => {
        return Math.round(value / timeSpent[index]);
      });
    });

    const rejectedCasesDividedByProduced = computed(() => {
      return rejectedCasesNormalized.value.map((rejected, index) => {
        const produced = producedCasesNormalized.value[index];
        return ((rejected / produced) * 100).toFixed(2);
      });
    });

    const timeSpentNormalized = computed(() => {
      const timeSpent = data.value?.y_axis_time_spend;

      if (timeSpent === undefined) {
        return [];
      }

      return timeSpent.map((value) => {
        if (isQuarterly.value) return value / 4;
        else return value;
      });
    });

    function fetch() {
      isFetching.value = true;
      // if model to or model from are null don't call api
      if (
        model.value?.from === null ||
        model.value?.from === undefined ||
        model.value?.to === null ||
        model.value?.to === undefined
      ) {
        isFetching.value = false;
        return;
      }

      void api
        .get(
          `average_speed_cases_hourly/${model.value?.from ?? ''}/${
            model.value?.to ?? ''
          }/${selectedLine.value}/${isQuarterly.value ? 'true' : 'false'}`
        )
        .then((res) => {
          // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
          data.value = res.data;
          console.log(res);
          isFetching.value = false;
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

    watch(isQuarterly, () => {
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
        const option: EChartOption = {
          title: {
            text: 'Average Line Speed Cases',
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'cross',
              crossStyle: {
                color: '#999',
              },
            },
            formatter(params) {
              if (!isArray(params)) {
                return '';
              }
              const numberOfOverillCases = params[0];
              const numberOfCasesProduced = params[1];
              const averageSpeed = params[2];
              const dataIndex = averageSpeed.dataIndex || 0;

              return `${numberOfOverillCases.marker || ''} ${
                numberOfOverillCases.seriesName || ''
              }: ${numberOfOverillCases.data as number}<br>
                      ${numberOfCasesProduced.marker || ''} ${
                numberOfCasesProduced.seriesName || ''
              }: ${numberOfCasesProduced.data as number}<br>
                ${averageSpeed.marker || ''} ${
                averageSpeed.seriesName || ''
              }: ${averageSpeed.data as number} hours <br>
              Rejected / Produced: ${
                rejectedCasesDividedByProduced.value[dataIndex] || ''
              }%`;
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
              'Number of cases produced',
              'Number of cases rejected',
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
              nameGap: 25,
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
              name: 'Number of cases produced',
              type: 'line',
              data: producedCasesNormalized.value,
            },
            {
              name: 'Number of cases rejected',
              type: 'line',
              data: rejectedCasesNormalized.value,
            },
            {
              name: 'Time spent',
              type: 'bar',
              data: timeSpentNormalized.value,
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
      isFetching,
      model,
      chartEl,
      lines,
      selectedLine,
      isQuarterly,
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

<style lang="sass" scoped>
.my-custom-toggle
  border: 1px solid #027be3
</style>
