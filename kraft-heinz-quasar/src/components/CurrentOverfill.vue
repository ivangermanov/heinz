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
    style="min-width: 290px"
    v-if="!isFetching"
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

    <q-select
      v-model="selectedOverfillType"
      label="Overfill Type"
      :options="overfillTypes"
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

    <q-btn-toggle
      v-model="isPast"
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
          {label: 'Past', value: true},
          {label: 'Present', value: false}
        ]"
    />

    <q-date
      v-if="isPast"
      v-model="model"
      range
      mask="DD-MM-YYYY"
    />

    <q-list
      v-if="!isPast"
      style="width: 100%"
    >
      <!--
        Rendering a <label> tag (notice tag="label")
        so QRadios will respond to clicks on QItems to
        change Toggle state.
      -->

      <q-item
        tag="label"
        v-ripple
      >
        <q-item-section avatar>
          <q-radio
            v-model="period"
            val="current_hour"
          />
        </q-item-section>
        <q-item-section>
          <q-item-label>Current Hour</q-item-label>
          <q-item-label
            caption
            v-if="data !== null"
          >{{ new Date(data.current_date[0]).getHours() }}-Now</q-item-label>
        </q-item-section>
      </q-item>

      <q-item
        tag="label"
        v-ripple
      >
        <q-item-section avatar>
          <q-radio
            v-model="period"
            val="current_shift"
          />
        </q-item-section>
        <q-item-section>
          <q-item-label>Current Shift</q-item-label>
          <q-item-label
            caption
            v-if="data !== null"
          >Shift {{ current_shift[0] }}</q-item-label>
        </q-item-section>
      </q-item>
    </q-list>

  </div>
  <q-card
    class="my-card"
    v-if="!isFetching"
  >
    <q-card-section class="bg-primary text-white">
      <div class="flex items-center justify-center text-h6">Overfill</div>
    </q-card-section>

    <q-separator />

    <q-card-section class="flex items-center justify-center text-h6">
      <span v-if="data !== null">{{period === "current_hour" ? data.overfill_value[0].toFixed(2) : data.overfill_values.toFixed(2)}} lbs</span>
    </q-card-section>

  </q-card>
</template>

<script lang="ts">
import { api } from 'src/boot/axios';
import { defineComponent, computed, watch, ref } from 'vue';
import { cloneDeep } from 'lodash';

interface CurrentOverfillDTO {
  current_date: string;
  overfill_value: number[];
  current_shift: string[];
  overfill_values: number;
}

const lineOptions = ['1', '3', '4', '5', '6', '7', '8', '11', '13', '14'];

const overfillTypes = [
  'Cumulative Overfill',
  'Absolute Overfill',
  'Overfill',
  'Underfill',
];

export default defineComponent({
  props: {},
  setup() {
    const data = ref(null as CurrentOverfillDTO | null);
    const isFetching = ref(true);

    const model = ref(null as typeof computedModel.value | null);
    const lines = ref(lineOptions);
    const selectedLine = ref(lineOptions[0]);

    const selectedOverfillType = ref(overfillTypes[0]);

    const isPast = ref(false);
    const period = ref('current_hour');

    function fetch() {
      if (isPast.value === true) {
        isFetching.value = true;
        void api
          .get(
            `current_overfill_past/${model.value?.from ?? ''}/${
              model.value?.to ?? ''
            }/${selectedLine.value}/${selectedOverfillType.value}`
          )
          .then((res) => {
            console.log(res);
            // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
            data.value = res.data;
            isFetching.value = false;
          });
      } else {
        isFetching.value = true;
        void api
          .get(
            `current_overfill_present/${selectedLine.value}/${selectedOverfillType.value}`
          )
          .then((res) => {
            console.log(res);
            // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
            data.value = res.data;
            isFetching.value = false;
          });
      }
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

    watch(selectedOverfillType, () => {
      fetch();
    });

    watch(isPast, () => {
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

    return {
      data,
      isFetching,
      model,
      lines,
      selectedLine,
      isPast,
      period,
      overfillTypes,
      selectedOverfillType,
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
.my-card
  width: 100%
  max-width: 400px

.my-custom-toggle
  border: 1px solid #027be3
</style>