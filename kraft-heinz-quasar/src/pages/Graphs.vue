<template>
  <q-page class="row items-center justify-evenly q-gutter-xl q-pa-md">
    <!-- Cases - Target vs Actual card -->
    <q-card
      class="col-3 cursor-pointer q-hoverable "
      v-ripple
    >
      <router-link
        to="/cases-target-vs-actual"
        style="text-decoration: none; color: inherit;"
      >
        <q-card-section>
          <div class="column items-center justify-center">
            <q-img
              src="cases-target-vs-actual.png"
              spinner-color="white"
            />
            <span class="q-pt-md non-selectable">
              Cases - Target vs Actual
            </span>
          </div>
        </q-card-section>
      </router-link>
    </q-card>
    <!-- SKUs over time -->
    <q-card
      class="col-3 cursor-pointer q-hoverable "
      v-ripple
    >
      <router-link
        to="/skus-over-time"
        style="text-decoration: none; color: inherit;"
      >
        <q-card-section>
          <div class="column items-center justify-center">
            <q-img
              src="skus-over-time.png"
              spinner-color="white"
            />
            <span class="q-pt-md non-selectable">
              SKUs Over Time
            </span>
          </div>
        </q-card-section>
      </router-link>
    </q-card>
    <!-- SKU Overfill heatmap -->
    <q-card
      class="col-3 cursor-pointer q-hoverable "
      v-ripple
    >
      <router-link
        to="/sku-overfill-heatmap"
        style="text-decoration: none; color: inherit;"
      >
        <q-card-section>
          <div class="column items-center justify-center">
            <q-img
              src="sku-overfill-heatmap.png"
              spinner-color="white"
            />
            <span class="q-pt-md non-selectable">
              SKU Overfill Heatmap
            </span>
          </div>
        </q-card-section>
      </router-link>
    </q-card>
    <!-- Line overfill heatmap -->
    <q-card
      class="col-3 cursor-pointer q-hoverable "
      v-ripple
    >
      <router-link
        to="/line-overfill-heatmap"
        style="text-decoration: none; color: inherit;"
      >
        <q-card-section>
          <div class="column items-center justify-center">
            <q-img
              src="line-overfill-heatmap.png"
              spinner-color="white"
            />
            <span class="q-pt-md non-selectable">
              Line Overfill Heatmap
            </span>
          </div>
        </q-card-section>
      </router-link>
    </q-card>
    <!-- Bar Line Average Speed Cases -->
    <q-card
      class="col-3 cursor-pointer q-hoverable "
      v-ripple
    >
      <router-link
        to="/bar-line-average-speed-cases"
        style="text-decoration: none; color: inherit;"
      >
        <q-card-section>
          <div class="column items-center justify-center">
            <q-img
              src="bar-line-average-speed-cases.png"
              spinner-color="white"
            />
            <span class="q-pt-md non-selectable">
              Bar Line Average Speed Cases
            </span>
          </div>
        </q-card-section>
      </router-link>
    </q-card>
    <!-- Bar Line SKU Family -->
    <q-card
      class="col-3 cursor-pointer q-hoverable "
      v-ripple
    >
      <router-link
        to="/bar-line-sku-family"
        style="text-decoration: none; color: inherit;"
      >
        <q-card-section>
          <div class="column items-center justify-center">
            <q-img
              src="bar-line-sku-family.png"
              spinner-color="white"
            />
            <span class="q-pt-md non-selectable">
              Bar Line Overfill Per SKU Family
            </span>
          </div>
        </q-card-section>
      </router-link>
    </q-card>
    <!-- Current overfill -->
    <q-card
      class="col-3 cursor-pointer q-hoverable "
      v-ripple
    >
      <router-link
        to="/current-overfill"
        style="text-decoration: none; color: inherit;"
      >
        <q-card-section>
          <div class="column items-center justify-center">
            <q-img
              src="current-overfill.png"
              spinner-color="white"
            />
            <span class="q-pt-md non-selectable">
              Current Overfill
            </span>
          </div>
        </q-card-section>
      </router-link>
    </q-card>
  </q-page>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  components: {},
  setup() {
    return {};
  },
});
</script>
