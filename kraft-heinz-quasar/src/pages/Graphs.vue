<template>
  <q-page class="row items-center justify-evenly">
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
    <!-- SKU heatmap -->
    <q-card
      class="col-3 cursor-pointer q-hoverable "
      v-ripple
    >
      <router-link
        to="/skus-heatmap"
        style="text-decoration: none; color: inherit;"
      >
        <q-card-section>
          <div class="column items-center justify-center">
            <q-img
              src="skus-heatmap.png"
              spinner-color="white"
            />
            <span class="q-pt-md non-selectable">
              SKUs Heatmap
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
