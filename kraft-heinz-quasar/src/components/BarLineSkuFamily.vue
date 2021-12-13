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
import { cloneDeep } from 'lodash';

interface BarLineSkuFamilyDTO {
  avg_speed_values: number[];
  hour_strings: string[];
  legend: string[];
  overfill_max: number;
  overfill_min: number;
  overfill_values: { [key: string]: number[] };
  speed_max: number;
  speed_min: number;
}

const lineOptions = ['1', '3', '4', '5', '6', '7', '8', '11', '13', '14'];

export default defineComponent({
  props: {},
  setup() {
    const data = ref(null as BarLineSkuFamilyDTO | null);
    const isFetching = ref(true);

    const model = ref(null as typeof computedModel.value | null);
    const lines = ref(lineOptions);
    const selectedLine = ref(lineOptions[0]);

    const isQuarterly = ref(true);

    const chart: Ref<echarts.ECharts | null> = shallowRef(null);
    const chartEl: Ref<HTMLElement | null> = ref(null);

    const overfillValuesSeries = computed(() => {
      if (data.value === null || data.value === undefined) {
        return [];
      }

      const overfillValues = data.value.overfill_values;
      const overfillValuesSeries: EChartOption.SeriesLine[] = [];

      Object.keys(overfillValues).forEach((key) => {
        overfillValuesSeries.push({
          name: key,
          type: 'bar',
          data: overfillValues[key],
        });
      });
      console.log(overfillValuesSeries);
      return overfillValuesSeries;
    });

    function fetch() {
      isFetching.value = true;
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
          `bar_line/${model.value?.from ?? ''}/${model.value?.to ?? ''}/${
            selectedLine.value
          }/${isQuarterly.value ? 'true' : 'false'}`
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
        from: '01-01-2021',
        to: '02-01-2021',
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
            text: 'Overfill Per SKU Family',
          },
          tooltip: {
            trigger: 'axis',
            axisPointer: {
              type: 'cross',
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
          legend: {
            data: [
              // 'Average speed',
              ...(data.value?.legend ?? []),
            ],
          },
          xAxis: [
            {
              type: 'category',
              data: data.value?.hour_strings.map((date) =>
                new Date(date).toLocaleString('en-US')
              ),
            },
          ],
          yAxis: [
            // {
            //   type: 'value',
            //   name: 'Average speed',
            //   min: data.value?.speed_min,
            //   max: data.value?.speed_max,
            // },
            {
              type: 'value',
              name: 'Overfill',
              min: data.value?.overfill_min,
              max: data.value?.overfill_max,
            },
          ],
          series: [
            // {
            //   name: 'Average speed',
            //   type: 'line',
            //   data: data.value?.avg_speed_values,
            // },
            ...overfillValuesSeries.value,
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
