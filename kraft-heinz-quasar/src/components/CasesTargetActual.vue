<template>
  <q-inner-loading
    :showing="data === null"
    label="Please wait..."
    color="primary"
    label-style="font-size: 1.1em"
    label-class="text-primary"
  />
  <div
    class="q-gutter-md row items-start"
    v-if="data !==null"
  >
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

interface TargetActualCasesDTO {
  'Cases Produced': number[];
  Date: string[];
  Target: number[];
}

export default defineComponent({
  props: {},
  setup() {
    const data = ref(null as TargetActualCasesDTO | null);

    const model = ref(null as typeof computedModel.value | null);
    // TODO: Pass actual line
    const line = ref(1);

    const chart: Ref<echarts.ECharts | null> = shallowRef(null);
    const chartEl: Ref<HTMLElement | null> = ref(null);

    watch(
      model,
      () => {
        void api
          .get(
            `target_actual_cases/${model.value?.from ?? ''}/${
              model.value?.to ?? ''
            }/${line.value}`
          )
          .then((res) => {
            console.log(res);
            // TODO: Make interface
            // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
            data.value = res.data;
          });
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
        const option = {
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
          yAxis: {},
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

    return { data, model, chartEl };
  },
});
</script>
