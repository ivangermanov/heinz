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
  Date: string[];
  SKU: string[];
}

export default defineComponent({
  props: {},
  setup() {
    const data = ref(null as TargetActualCasesDTO | null);

    const model = ref(null as typeof computedModel.value | null);
    const line = ref(1);

    const chart: Ref<echarts.ECharts | null> = shallowRef(null);
    const chartEl: Ref<HTMLElement | null> = ref(null);

    watch(
      model,
      () => {
        void api
          .get(
            `sku/${model.value?.from ?? ''}/${model.value?.to ?? ''}/${
              line.value
            }`
          )
          .then((res) => {
            console.log(res);
            // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
            data.value = res.data;
          });
      },
      { deep: true }
    );

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
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow',
            },
          },
          title: {
            text: 'SKUs Over Time - Line 3',
          },
          toolbox: {
            feature: {
              saveAsImage: {},
              dataView: {},
            },
          },
          dataZoom: [
            {
              type: 'slider',
              start: 0,
              end: 100,
            },
            {
              type: 'inside',
              start: 0,
              end: 100,
            },
          ],
          xAxis: {
            data: data.value?.Date.map((date) =>
              new Date(date).toLocaleString('en-US')
            ),
          },
          yAxis: {
            name: 'SKU',
            type: 'category',
          },
          series: [
            {
              type: 'scatter',
              name: 'SKU',
              data: data.value?.SKU,
              itemStyle: {
                color: '#77bef7',
              },
              symbolSize: 5,
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
