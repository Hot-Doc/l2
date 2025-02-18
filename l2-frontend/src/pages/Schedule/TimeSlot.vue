<template>
  <div
    class="slot"
    :class="[`slot-status-${data.status}`, mode === 'list' ? 'slot-list' : 'slot-natural']"
    :style="mode === 'list' ? '' : `top: ${offset}; min-height: ${minHeight};`"
  >
    <div
      class="slot-inner"
      @click="open"
    >
      <div
        v-if="data.patient"
        class="patient-row"
      >
        <strong v-if="data.cito">CITO</strong> <span>{{ smallTime(data.time) }}</span>
        <span class="fio">{{ data.patient.fioShort }}</span>
      </div>
      <div
        v-else
        class="patient-row"
      >
        <span>{{ smallTime(data.time) }}</span>
      </div>
      <div
        v-if="data.service && data.service.id"
        class="service-row"
      >
        {{ data.service.title }}
      </div>
      <div class="param-row">
        <i class="far fa-circle" /> {{ data.duration }} мин
      </div>
    </div>

    <MountingPortal
      mount-to="#portal-place-modal"
      :name="`TimeSlotPopup-${smallTime(data.time)}—${data.date}`"
      append
    >
      <transition name="fade">
        <modal
          v-if="isOpened"
          show-footer="true"
          white-bg="true"
          max-width="710px"
          width="100%"
          margin-left-right="auto"
          @close="close"
        >
          <span slot="header">{{ data.date }} {{ data.time }}</span>
          <div
            slot="body"
            class="popup-body"
          >
            <div
              v-if="!details"
              class="preloader"
            >
              <i class="fa fa-spinner" /> загрузка
            </div>
            <div v-else>
              <div class="patient-root">
                <PatientSmallPicker
                  v-model="details.cardId"
                  :base_pk="details.baseId"
                />
              </div>
              <div
                v-if="details.cardId"
                class="form-row"
              >
                <div class="row-t">
                  Услуга
                </div>
                <div class="row-v">
                  <treeselect
                    v-model="details.service.id"
                    class="treeselect-noborder"
                    :multiple="false"
                    :disable-branch-nodes="true"
                    :options="services"
                    placeholder="Услуга не выбрана"
                  />
                </div>
              </div>
            </div>
          </div>
          <div slot="footer">
            <div class="row">
              <div class="col-xs-6">
                <button
                  class="btn btn-blue-nb"
                  type="button"
                  @click="close"
                >
                  Закрыть
                </button>
              </div>
              <div class="col-xs-6">
                <button
                  class="btn btn-blue-nb"
                  type="button"
                  @click="save"
                >
                  Сохранить
                </button>
              </div>
            </div>
          </div>
        </modal>
      </transition>
    </MountingPortal>
  </div>
</template>

<script lang="ts">
import Vue from 'vue';
import Component from 'vue-class-component';
import Treeselect from '@riophae/vue-treeselect';

import '@riophae/vue-treeselect/dist/vue-treeselect.css';
import * as actions from '@/store/action-types';
import Modal from '@/ui-cards/Modal.vue';
import PatientSmallPicker from '@/ui-cards/PatientSmallPicker.vue';

@Component({
  components: {
    Modal,
    PatientSmallPicker,
    Treeselect,
  },
  props: {
    data: {
      type: Object,
      required: true,
    },
    allHoursValues: {
      type: Array,
      required: true,
    },
    mode: {
      type: String,
    },
    services: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      isOpened: false,
      details: null,
      selectedCard: {},
    };
  },
  watch: {
    cardId(n, p) {
      if (n && !p && this.services?.length === 1) {
        this.details.service.id = this.services[0].id;
      }
    },
  },
})
export default class TimeSlot extends Vue {
  data: any;

  details: any;

  selectedCard: any;

  allHoursValues: any[];

  isOpened: boolean;

  mode: string | null;

  services: any[];

  get cardId() {
    return this.details?.cardId;
  }

  get offset() {
    const offset = this.data.minute * 2 + this.allHoursValues.indexOf(this.data.hourValue) * 120 + 51;
    return `${offset}px`;
  }

  get minHeight() {
    return `${this.data.duration * 2}px`;
  }

  async loadData() {
    this.details = null;
    await this.$store.dispatch(actions.INC_LOADING);
    const { ok, data } = await this.$api('/schedule/details', this.data, 'id');
    this.details = data;

    if (!ok) {
      this.close();
      this.$root.$emit('msg', 'error', 'Не удалось загрузить данные!');
    } else if (this.details.patient) {
      setTimeout(() => {
        this.$root.$emit('select_card', this.details.patient);
        this.$store.dispatch(actions.DEC_LOADING);
      }, 200);
      return;
    }

    await this.$store.dispatch(actions.DEC_LOADING);
  }

  // eslint-disable-next-line class-methods-use-this
  smallTime(t) {
    const [h, m] = t.split(':');
    return `${h}:${m}`;
  }

  open() {
    this.isOpened = true;
    this.loadData();
  }

  close() {
    this.isOpened = false;
  }

  async save() {
    await this.$store.dispatch(actions.INC_LOADING);
    const { ok, message } = await this.$api('/schedule/save', {
      ...this.data,
      ...this.details,
      serviceId: this.details.service.id,
    });

    if (ok) {
      this.$root.$emit('msg', 'ok', 'Сохранено');
      this.close();
    } else {
      this.$root.$emit('msg', 'error', message);
    }

    this.$root.$emit('reload-slots');

    await this.$store.dispatch(actions.DEC_LOADING);
  }
}
</script>

<style lang="scss" scoped>
$slot-minimal-height: 12px;
$slot-minimal-height-opened: 60px;
$slot-left-offset: 38px;
$slot-padding: 2px;

.patient-root {
  height: 110px;
}

.preloader {
  text-align: center;
  padding: 20px;
}

.patient-row,
.service-row,
.param-row {
  white-space: nowrap;
  overflow: hidden;

  font-size: 12px;
}

.patient-row + .param-row,
.service-row + .param-row,
.param-row + .param-row,
.param-row + .patient-row,
.param-row + .service-row {
  margin-top: 1px;
  padding-top: 1px;
  border-top: 1px solid #34343488;
}

.param-row {
  padding: 0 2px;
  line-height: 14px;

  .fa {
    font-size: 10px;
  }
}

.patient-row .fio {
  font-weight: bold;
}

.slot {
  cursor: pointer;

  &.slot-natural {
    position: absolute;

    left: $slot-left-offset;
    right: 0;
    z-index: 1;
  }

  &-inner {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    padding: $slot-padding $slot-padding * 2;
  }

  border-radius: $slot-padding * 2;
  min-height: $slot-minimal-height;
  line-height: 1;

  &,
  &-inner {
    transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
  }

  &,
  &:hover .slot-inner {
    border: 1px solid rgb(176, 176, 176);
    background: linear-gradient(to bottom, rgb(250, 250, 250) 0%, rgb(219, 219, 219) 100%);
  }

  &-list {
    min-height: 32px;
    margin-bottom: 3px;
    position: relative;
    overflow: hidden;
  }

  &:hover {
    box-shadow: 0 14px 28px rgba(0, 0, 0, 0.25), 0 10px 10px rgba(0, 0, 0, 0.22);
    z-index: 2;
    transform: scale(1.016);
    &.slot-natural {
      min-height: $slot-minimal-height-opened;
    }

    &.slot-list {
      overflow: visible;
    }

    .patient-row,
    .service-row,
    .param-row {
      white-space: unset;
    }

    .slot-inner {
      box-shadow: 0 14px 28px rgba(0, 0, 0, 0.25), 0 10px 10px rgba(0, 0, 0, 0.22);
      bottom: unset;
    }
  }

  &-status {
    &-empty {
      &,
      & .slot-inner {
        color: #fff;
        border-color: #049372 !important;
        background: linear-gradient(to bottom, #04937288 0%, #049372dd 100%) !important;

        &:hover {
          background: linear-gradient(to bottom, #049372bb 0%, #049372ee 100%) !important;
        }
      }
    }
    &-reserved {
      &,
      & .slot-inner {
        color: #fff;
        border: 1px solid #932a04 !important;
        background: linear-gradient(to bottom, #932a0488 0%, #932a04dd 100%) !important;
        &:hover {
          background: linear-gradient(to bottom, #932a04bb 0%, #932a04ee 100%) !important;
        }
      }
    }
    &-cancelled {
      &,
      & .slot-inner {
        border: 1px solid rgba(0, 0, 0, 0.14) !important;
        background-image: linear-gradient(#6c7a89, #56616c) !important;
      }
    }
    // &-success {
    // }
  }
}

.popup-body {
  min-height: 350px;
}

.form-row {
  width: 100%;
  display: flex;
  border-bottom: 1px solid #434a54;

  &:first-child:not(.nbt-i) {
    border-top: 1px solid #434a54;
  }

  justify-content: stretch;

  .row-t {
    background-color: #aab2bd;
    padding: 7px 0 0 10px;
    width: 35%;
    flex: 0 35%;
    color: #fff;
  }

  .input-group {
    flex: 0 65%;
  }

  input,
  .row-v,
  ::v-deep input {
    background: #fff;
    border: none;
    border-radius: 0 !important;
    width: 60%;
    flex: 0 65%;
    height: 36px;
  }

  &.sm-f {
    .row-t {
      padding: 2px 0 0 10px;
    }

    input,
    .row-v,
    ::v-deep input {
      height: 26px;
    }
  }

  ::v-deep input {
    width: 100% !important;
  }

  .row-v {
    padding: 0 0 0 0;
  }

  ::v-deep .input-group {
    border-radius: 0;
  }
}
</style>
