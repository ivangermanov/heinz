<template>
  <q-page class="row items-center justify-evenly">
    <cases-target-actual />
  </q-page>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import CasesTargetActual from 'src/components/CasesTargetActual.vue';

export default defineComponent({
  components: {
    CasesTargetActual,
  },
});
</script>
