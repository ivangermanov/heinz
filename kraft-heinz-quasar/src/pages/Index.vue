<template>
  <q-page class="row items-center justify-evenly">
    <xg-boost />
  </q-page>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import XgBoost from '@/components/XgBoost.vue';

export default defineComponent({
  components: {
    XgBoost,
  },
  setup() {
    return {};
  },
});
</script>
