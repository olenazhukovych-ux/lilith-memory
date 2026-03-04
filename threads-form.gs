function createThreadsForm() {
  var form = FormApp.create('Запис на супровід проєкту в Threads');
  
  form.setDescription('Привіт! Це форма для запису на супровід вашого проєкту в Threads.\n\nМи з командою допоможемо вам побудувати впізнаваність та підвищити продажі через щирі тексти та стратегічний маркетинг у цій соцмережі.\n\nЗаповніть ці кілька полів, щоб ми ближче познайомились. Після цього ми зв\'яжемось з вами протягом 24 годин, щоб обговорити взаємодію за онлайн-кавою ☕️');

  form.addTextItem()
    .setTitle('Ім\'я')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Контакт для зв\'язку у Telegram')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Назва бренду, з яким працюємо')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Посилання на соцмережі бренду')
    .setRequired(true);

  form.addCheckboxItem()
    .setTitle('Який результат хочете отримати від ведення Threads?')
    .setChoiceValues([
      'Побудова особистого бренду',
      'Збільшення продажів',
      'Підвищення лояльності аудиторії',
      'Просування стартапу',
      'Інше'
    ])
    .setRequired(true);

  form.addTextItem()
    .setTitle('Який ваш орієнтовний бюджет на ведення Threads на місяць?')
    .setRequired(true);

  Logger.log('Форму створено: ' + form.getEditUrl());
  Logger.log('Посилання для заповнення: ' + form.getPublishedUrl());
}
