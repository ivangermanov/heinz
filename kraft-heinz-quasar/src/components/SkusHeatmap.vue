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
      use-input
      v-model="selectedSku"
      label="SKU"
      :options="skus"
      @filter="filterFn"
      style="width: 300px"
    >
      <template v-slot:no-option>
        <q-item>
          <q-item-section class="text-grey">
            No results
          </q-item-section>
        </q-item>
      </template>
    </q-select>
  </div>

  <div
    v-if="data !==null"
    ref="chartEl"
    style="width: 60%; height: 500px"
  />
</template>

<script lang="ts">
import { api } from 'src/boot/axios';
import {
  defineComponent,
  computed,
  watch,
  Ref,
  ref,
  shallowRef,
  onBeforeMount,
} from 'vue';
import * as echarts from 'echarts';

interface SkusHeatmapDTO {
  Date: string[];
  Lines: string[];
  data: number[][];
  max_colorcode: number;
  min_colorcode: number;
}

export default defineComponent({
  props: {},
  setup() {
    const data = ref(null as SkusHeatmapDTO | null);
    const skuOptions = ref<string[]>([]);
    const skus = ref(skuOptions.value);
    const selectedSku = ref(skuOptions.value[0]);

    const chart: Ref<echarts.ECharts | null> = shallowRef(null);
    const chartEl: Ref<HTMLElement | null> = ref(null);

    const computedMap = computed(() => {
      if (!data.value) return [];

      return data.value.data.map((item) => {
        return [item[0], item[1], item[2] || '-'];
      });
    });

    onBeforeMount(() => {
      fetchAllSkus();
    });

    function fetchAllSkus() {
      void api.get('/get_all_skus').then((res) => {
        console.log(res);
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        skuOptions.value = res.data;
      });
    }

    function fetchHeatmap() {
      void api.get(`/sku_overfill_heat/${selectedSku.value}`).then((res) => {
        console.log(res);
        // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
        data.value = res.data;
      });
    }

    watch(selectedSku, () => {
      fetchHeatmap();
    });

    watch(skuOptions, () => {
      skus.value = skuOptions.value;
      selectedSku.value = skuOptions.value[0];
      fetchHeatmap();
    });

    watch(
      [data, chartEl],
      () => {
        const option = {
          title: {
            text: 'Heatmap of SKU Overfill Over Time',
          },
          tooltip: {
            position: 'top',
          },
          xAxis: {
            type: 'category',
            data: data.value?.Date.map((date) =>
              new Date(date).toLocaleString('en-US')
            ),
            splitArea: {
              show: true,
            },
          },
          yAxis: {
            type: 'category',
            name: 'Line',
            data: data.value?.Lines,
            splitArea: {
              show: true,
            },
          },
          visualMap: {
            min: data.value?.min_colorcode,
            max: data.value?.max_colorcode,
            calculable: true,
            orient: 'vertical',
            right: 0,
            top: 50,
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
          series: [
            {
              name: 'Overfill',
              type: 'heatmap',
              data: computedMap.value,
              label: {
                show: false,
              },
              emphasis: {
                itemStyle: {
                  shadowBlur: 10,
                  shadowColor: 'rgba(0, 0, 0, 0.5)',
                },
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
      chartEl,
      skuOptions,
      skus,
      selectedSku,
      filterFn(val: string, update: (arg0: () => void) => void) {
        update(() => {
          const needle = val.toLowerCase();
          skus.value = skuOptions.value.filter(
            (v) => v.toLowerCase().indexOf(needle) > -1
          );
        });
      },
    };
  },
});
</script>
