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
import { EChartOption } from 'echarts';

interface TargetActualCasesDTO {
  'Cases Produced': number[];
  Date: string[];
  Target: number[];
}

const lineOptions = ['1', '3', '4', '5', '6', '7', '8', '11', '13', '14'];

export default defineComponent({
  props: {},
  setup() {
    const data = ref(null as TargetActualCasesDTO | null);

    const model = ref(null as typeof computedModel.value | null);
    const lines = ref(lineOptions);
    const selectedLine = ref(lineOptions[0]);

    const chart: Ref<echarts.ECharts | null> = shallowRef(null);
    const chartEl: Ref<HTMLElement | null> = ref(null);

    function fetch() {
      void api
        .get(
          `target_actual_cases/${model.value?.from ?? ''}/${
            model.value?.to ?? ''
          }/${selectedLine.value}`
        )
        .then((res) => {
          console.log(res);
          // TODO: Make interface
          // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
          data.value = res.data;
        });
    }

    watch(selectedLine, () => {
      fetch();
    });

    watch(
      model,
      () => {
        fetch();
      },
      { deep: true }
    );

    const computedModel = computed(() => {
      return {
        from: '08-04-2019',
        to: '08-04-2022',
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
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow',
            },
          },
          title: {
            text: 'Cases - Target vs Actual',
          },
          legend: {
            data: ['Actual', 'Target'],
          },
          toolbox: {
            feature: {
              saveAsImage: {},
              magicType: {
                type: ['stack', 'bar', 'line'],
              },
              dataView: {},
            },
          },
          dataZoom: [
            {
              type: 'slider',
              start: 69,
              end: 70,
            },
            {
              type: 'inside',
              start: 69,
              end: 70,
            },
          ],
          xAxis: {
            data: data.value?.Date.map((date) =>
              new Date(date).toLocaleString('en-US')
            ),
          },
          yAxis: {
            name: 'Number of cases',
          },
          series: [
            {
              type: 'bar',
              name: 'Actual',
              data: data.value?.['Cases Produced'],
              itemStyle: {
                color: '#77bef7',
              },
            },
            {
              type: 'bar',
              name: 'Target',
              data: data.value?.Target,
              itemStyle: {
                color: '#e46c0b',
              },
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
