export default [
  {url: '/forms/pdf?type=101.02&card_pk={card}', title: 'Согласие на обработку персональных данных'},
  {url: '/forms/pdf?type=101.03&card_pk={card}', title: 'Согласие на медицинское вмешательство'},
  {url: '/forms/pdf?type=101.01&individual={individual}', title: 'Согласие на ВИЧ-исследование', not_internal: true},
  {url: '/forms/pdf?type=100.01&card_pk={card}', title: 'Паспорт здоровья'},
  {url: '/forms/pdf?type=100.02&card_pk={card}', title: 'Титульный лист карты, 025/у'},
];

export const forDirs = [
  {url: '/forms/pdf?type=102.01&card_pk={card}&napr_id={dir}', title: 'Договор', need_dirs: true},
];

export const form112 = [
  {url: '/forms/pdf?type=108.01&card_pk={card}', title: ' Ф.112'}
];

export const planOperations = [
  {url: '/forms/pdf?type=109.01&pks_plan={pks_plan}', title: ' План операций'}
];
