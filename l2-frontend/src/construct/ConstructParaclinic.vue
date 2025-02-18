<template>
  <div
    ref="root"
    class="construct-root"
  >
    <div
      v-show="opened_id === -2"
      v-if="departments_of_type.length > 0"
      class="construct-sidebar"
    >
      <div class="sidebar-select">
        <SelectPickerB
          v-model="department"
          style="height: 34px"
          :options="departments_of_type"
        />
      </div>
      <input
        v-model="title_filter"
        class="form-control"
        style="padding-top: 7px; padding-bottom: 7px"
        placeholder="Фильтр по названию"
      >
      <div
        class="sidebar-content"
        :class="{ fcenter: researches_list_filtered.length === 0 }"
      >
        <div v-if="researches_list_filtered.length === 0">
          Не найдено
        </div>
        <div
          v-for="row in researches_list_filtered"
          :key="row.pk"
          class="research"
          :class="{ rhide: row.hide }"
          @click="open_editor(row.pk)"
        >
          {{ row.title }}
        </div>
      </div>
      <button
        class="btn btn-blue-nb sidebar-footer"
        @click="open_editor(-1)"
      >
        <i class="glyphicon glyphicon-plus" />
        Добавить
      </button>
    </div>
    <div
      v-if="parseInt(department, 10) <= -500 && parseInt(department, 10) > -600"
      class="construct-content"
    >
      <StationarFormEditor
        v-if="opened_id > -2"
        style="position: absolute; top: 0; right: 0; bottom: 0; left: 0"
        :pk="opened_id"
        :department="department_int"
        :direction_forms="direction_forms"
      />
    </div>
    <div
      v-else-if="department !== '-6'"
      class="construct-content"
    >
      <ParaclinicResearchEditor
        v-if="opened_id > -2"
        style="position: absolute; top: 0; right: 0; bottom: 0; left: 0"
        :pk="opened_id"
        :department="department_int"
        :direction_forms="direction_forms"
        :result_forms="result_forms"
        :specialities="specialities"
        :permanent_directories="permanent_directories"
        :period_types="period_types"
      />
    </div>
    <div
      v-else
      class="construct-content"
    >
      <MicrobiologyResearchEditor
        v-if="opened_id > -2"
        :department="department_int"
        :pk="opened_id"
        :direction_forms="direction_forms"
        style="position: absolute; top: 0; right: 0; bottom: 0; left: 0"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { mapGetters } from 'vuex';

import SelectPickerB from '@/fields/SelectPickerM.vue';
import researchesPoint from '@/api/researches-point';
import * as actions from '@/store/action-types';

import ParaclinicResearchEditor from './ParaclinicResearchEditor.vue';
import MicrobiologyResearchEditor from './MicrobiologyResearchEditor.vue';
import StationarFormEditor from './StationarFormEditor.vue';

export default {
  name: 'ConstructParaclinic',
  components: {
    StationarFormEditor,
    SelectPickerB,
    ParaclinicResearchEditor,
    MicrobiologyResearchEditor,
  },
  data() {
    return {
      department: '-1',
      // departments: [],
      researches_list: [],
      departments_of_type: [],
      opened_id: -2,
      title_filter: '',
      direction_forms: [],
      result_forms: [],
      specialities: [],
      permanent_directories: {},
      period_types: [],
    };
  },
  computed: {
    department_int() {
      return parseInt(this.department, 10);
    },
    researches_list_filtered() {
      if (!this.researches_list) {
        return [];
      }
      return this.researches_list.filter(
        (row) => row.title.trim().toLowerCase().indexOf(this.title_filter.trim().toLowerCase()) >= 0,
      );
    },
    ...mapGetters({
      departments: 'allDepartments',
      modules: 'modules',
    }),
    can_edit_stationar() {
      for (const g of this.$store.getters.user_data.groups || []) {
        if (g === 'Редактирование стационара') {
          return true;
        }
      }
      return false;
    },
  },
  watch: {
    department: {
      handler() {
        if (['-1', '-9998'].includes(this.department)) return;
        this.load_researches();
      },
      immediate: true,
    },
    modules: {
      handler() {
        this.update_deps();
      },
      deep: true,
      immediate: true,
    },
    departments: {
      handler() {
        this.update_deps();
      },
      deep: true,
      immediate: true,
    },
  },
  mounted() {
    this.$root.$on('research-editor:cancel', this.cancel_edit);
    this.$store.watch(
      (state) => state.user.data,
      () => {
        this.update_deps();
      },
    );
    this.update_deps();
  },
  methods: {
    load_researches() {
      this.$store.dispatch(actions.INC_LOADING);
      researchesPoint
        .getResearchesByDepartment(this, 'department')
        .then((data) => {
          this.researches_list = data.researches;
          this.direction_forms = data.direction_forms;
          this.result_forms = data.result_forms;
          this.specialities = data.specialities;
          this.permanent_directories = data.permanent_directories;
          this.period_types = data.period_types;
        })
        .finally(() => {
          this.$store.dispatch(actions.DEC_LOADING);
        });
    },
    open_editor(pk) {
      if (pk === -9998) {
        return;
      }
      this.opened_id = pk;
    },
    cancel_edit() {
      this.opened_id = -2;
      this.load_researches();
    },
    update_deps() {
      if (this.departments.length === 0 || !this.$store.getters.user_data || !this.$store.getters.user_data.department) {
        return;
      }

      const d = [];
      if (Object.keys(this.modules).length > 0) {
        for (const row of this.departments) {
          if (row.type === '3') {
            d.push({ label: row.title, value: row.pk });
            if (row.pk.toString() === this.$store.getters.user_data.department.pk.toString() && this.department === '-1') {
              this.department = row.pk.toString();
            }
          }
        }

        if (this.modules.consults_module) {
          d.push({ value: -2, label: 'Консультации' });
        }

        if (this.modules.l2_treatment) {
          d.push({ value: -3, label: 'Лечение' });
        }

        if (this.modules.l2_stom) {
          d.push({ value: -4, label: 'Стоматология' });
        }
        if (this.modules.l2_forms) {
          d.push({ value: -9, label: 'Формы' });
        }
        if (this.modules.l2_applications) {
          d.push({ value: -11, label: '– Заявления' });
        }
        if (this.modules.directions_params) {
          d.push({ value: -10, label: 'Параметры направления' });
        }
        if (this.modules.l2_monitorings) {
          d.push({ value: -12, label: 'Мониторинги' });
        }
        if (this.modules.l2_expertise) {
          d.push({ value: -13, label: 'Экспертиза' });
        }

        if (this.modules.l2_hosp && this.can_edit_stationar) {
          d.push({ value: -5, label: 'Стационар' });
          d.push({ value: -500, label: '– Первичный прием' });
          d.push({ value: -501, label: '– Дневник' });
          d.push({ value: -502, label: '– ВК' });
          d.push({ value: -503, label: '– Операции' });
          d.push({ value: -504, label: '– Фармакотерапия' });
          d.push({ value: -505, label: '– Физиотерапия' });
          d.push({ value: -506, label: '– Эпикриз' });
          d.push({ value: -507, label: '– Выписка' });
          d.push({ value: -508, label: '– Больничный лист' });
          d.push({ value: -509, label: '– t, ad, p – лист' });
        }

        if (this.modules.morfology) {
          d.push({ value: -9998, label: 'Морфология' });
          if (this.modules.l2_microbiology) {
            d.push({ value: -6, label: '– Микробиология' });
          }
          if (this.modules.l2_citology) {
            d.push({ value: -7, label: '– Цитология' });
          }
          if (this.modules.l2_gistology) {
            d.push({ value: -8, label: '– Гистология' });
          }
        }
      }

      this.departments_of_type = d;

      this.set_dep();
    },
    set_dep(deps) {
      if (this.department !== '-1' || !deps || deps.length === 0 || !this.$store.getters.user_data.department) return;
      for (const row of deps) {
        if (row.value.toString() === this.$store.getters.user_data.department.pk.toString()) {
          this.department = row.value.toString();
          return;
        }
      }
      this.department = deps[0].value.toString();
    },
  },
};
</script>

<style scoped lang="scss">
.construct-root {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;

  display: flex;
  align-items: stretch;
  flex-direction: row;
  flex-wrap: nowrap;
  align-content: stretch;

  & > div {
    align-self: stretch;
  }
}

.construct-sidebar {
  width: 350px;
  border-right: 1px solid #b1b1b1;
  display: flex;
  flex-direction: column;

  .form-control {
    border-radius: 0;
    border-top: none;
    border-left: none;
    border-right: none;
  }
}

.construct-content {
  width: 100%;
  position: relative;
}

.sidebar-select ::v-deep .btn {
  border-radius: 0;
  border-top: none;
  border-left: none;
  border-right: none;
  border-top: 1px solid #fff;
}

.sidebar-select,
.sidebar-filter,
.sidebar-footer {
  flex: 0 0 34px;
}

.sidebar-content {
  height: 100%;
  overflow-y: auto;
  background-color: hsla(30, 3%, 97%, 1);
}

.sidebar-content:not(.fcenter) {
  padding-bottom: 10px;
}

.sidebar-footer {
  border-radius: 0;
  margin: 0;
}

.fcenter {
  display: flex;
  align-items: center;
  justify-content: center;
}

.research {
  background-color: #fff;
  padding: 5px;
  margin: 10px;
  border-radius: 4px;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
  transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1);
  position: relative;

  &.rhide {
    background-image: linear-gradient(#6c7a89, #56616c);
    color: #fff;
  }

  &:hover {
    box-shadow: 0 14px 28px rgba(0, 0, 0, 0.25), 0 10px 10px rgba(0, 0, 0, 0.22);
    z-index: 1;
    transform: scale(1.008);
  }
}

.research:not(:first-child) {
  margin-top: 0;
}

.research:last-child {
  margin-bottom: 0;
}
</style>
