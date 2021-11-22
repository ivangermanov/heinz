<template>
  <div>

  </div>
</template>

<script lang="ts">
/* eslint-disable @typescript-eslint/no-unsafe-call */
/* eslint-disable @typescript-eslint/no-unsafe-member-access */
/* eslint-disable @typescript-eslint/no-var-requires */

import { api } from 'src/boot/axios';
import { defineComponent } from 'vue';

export default defineComponent({
  props: {},
  setup() {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    // require('ml-xgboost').then((XGBoost: any) => {
    //   console.log(XGBoost);
    // });

    void api.get('todo').then((res) => {
      console.log(res);
    });

    return {};
  },
});
</script>
