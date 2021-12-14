import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [{ path: '', component: () => import('pages/Graphs.vue') }],
  },
  {
    path: '/cases-target-vs-actual',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '/cases-target-vs-actual',
        component: () => import('pages/CasesTargetActual.vue'),
      },
    ],
  },
  {
    path: '/skus-over-time',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '/skus-over-time',
        component: () => import('pages/SkusOverTime.vue'),
      },
    ],
  },
  {
    path: '/predict',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '/predict', component: () => import('pages/Predict.vue') },
    ],
  },
  {
    path: '/sku-overfill-heatmap',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '/sku-overfill-heatmap',
        component: () => import('src/pages/SkuOverfillHeatmap.vue'),
      },
    ],
  },
  {
    path: '/line-overfill-heatmap',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '/line-overfill-heatmap',
        component: () => import('src/pages/LineOverfillHeatmap.vue'),
      },
    ],
  },
  {
    path: '/bar-line-average-speed-cases',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '/bar-line-average-speed-cases',
        component: () => import('src/pages/BarLineAverageSpeedCases.vue'),
      },
    ],
  },
  {
    path: '/bar-line-sku-family',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '/bar-line-sku-family',
        component: () => import('src/pages/BarLineSkuFamily.vue'),
      },
    ],
  },
  {
    path: '/current-overfill',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '/current-overfill',
        component: () => import('src/pages/CurrentOverfill.vue'),
      },
    ],
  },
  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/Error404.vue'),
  },
];

export default routes;
