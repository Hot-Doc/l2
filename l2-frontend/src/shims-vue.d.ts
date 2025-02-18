declare module '*.vue' {
  import V from 'vue';

  declare module 'vue/types/vue' {
    interface Vue {
      $dialog: any;
      $api: (point: string, ctx?: any, pickKeys?: any, moreData?: any, formData?: FormData | null) => Promise<any>;
      $fullscreen: any;
      $systemTitle: () => string;
      $asVI: () => boolean;
      $l2LogoClass: () => string;
    }
  }

  export default V;
}

declare module '*.mp3' {
  const src: string;
  export default src;
}

declare module '@riophae/vue-treeselect' {
  export default V;

  export const ASYNC_SEARCH: any;
}
