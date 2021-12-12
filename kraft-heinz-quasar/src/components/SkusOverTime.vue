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

interface TargetActualCasesDTO {
  Date: string[];
  SKU: string[];
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
          `sku/${model.value?.from ?? ''}/${model.value?.to ?? ''}/${
            selectedLine.value
          }`
        )
        .then((res) => {
          console.log(res);
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
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'shadow',
            },
          },
          grid: { left: '200px' },
          title: {
            text: 'SKUs Over Time',
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
            axisLabel: {
              margin: 20,
              width: 180,
              overflow: 'truncate',
            },
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
