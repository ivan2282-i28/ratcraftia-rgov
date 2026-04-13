import 'package:flutter/material.dart';
import 'package:qr_flutter/qr_flutter.dart';

import '../core/ui.dart';
import '../services/api_client.dart';
import '../services/push_notification_service.dart';

class OverviewPage extends StatelessWidget {
  const OverviewPage({
    super.key,
    required this.loading,
    required this.busy,
    required this.profile,
    required this.did,
    required this.inbox,
    required this.news,
    required this.laws,
    required this.bills,
    required this.referenda,
    required this.loginChangeController,
    required this.onChangeLogin,
    required this.currentPasswordController,
    required this.newPasswordController,
    required this.confirmPasswordController,
    required this.onChangePassword,
    required this.pushStatus,
    required this.onEnablePush,
    required this.onDisablePush,
    required this.onPreviewPush,
  });

  final bool loading;
  final bool busy;
  final JsonMap? profile;
  final JsonMap? did;
  final List<JsonMap> inbox;
  final List<JsonMap> news;
  final List<JsonMap> laws;
  final List<JsonMap> bills;
  final List<JsonMap> referenda;
  final TextEditingController loginChangeController;
  final VoidCallback onChangeLogin;
  final TextEditingController currentPasswordController;
  final TextEditingController newPasswordController;
  final TextEditingController confirmPasswordController;
  final VoidCallback onChangePassword;
  final PushNotificationStatus pushStatus;
  final VoidCallback onEnablePush;
  final VoidCallback onDisablePush;
  final VoidCallback onPreviewPush;

  @override
  Widget build(BuildContext context) {
    return PageBody(
      loading: loading,
      children: [
        AdaptivePaneGrid(
          minChildWidth: 320,
          children: [
            _DidCard(profile: profile, did: did),
            const _HierarchyCard(),
            SectionCard(
              title: 'Профиль доступа',
              subtitle:
                  'Авторизация через JWT. Логин можно менять только один раз в сутки.',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  InfoRow(
                    label: 'Права доступа',
                    value:
                        profile?['permissions_label']?.toString() ??
                        'Не указано',
                  ),
                  InfoRow(
                    label: 'Логин',
                    value: profile?['login']?.toString() ?? 'Не указано',
                  ),
                  InfoRow(
                    label: 'Смена логина',
                    value: formatTimestamp(profile?['next_login_change_at']),
                  ),
                  const SizedBox(height: 18),
                  TextField(
                    controller: loginChangeController,
                    decoration: const InputDecoration(
                      labelText: 'Новый логин',
                      hintText: 'Например: citizen.portal',
                    ),
                  ),
                  const SizedBox(height: 12),
                  FilledButton.tonal(
                    onPressed: busy ? null : onChangeLogin,
                    child: const Text('Обновить логин'),
                  ),
                  const SizedBox(height: 18),
                  Text(
                    'Смена пароля',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      color: appTextColor(context),
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: currentPasswordController,
                    obscureText: true,
                    decoration: const InputDecoration(
                      labelText: 'Текущий пароль',
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: newPasswordController,
                    obscureText: true,
                    decoration: const InputDecoration(
                      labelText: 'Новый пароль',
                      hintText: 'Минимум 6 символов',
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: confirmPasswordController,
                    obscureText: true,
                    decoration: const InputDecoration(
                      labelText: 'Повторите новый пароль',
                    ),
                  ),
                  const SizedBox(height: 12),
                  FilledButton.tonal(
                    onPressed: busy ? null : onChangePassword,
                    child: const Text('Обновить пароль'),
                  ),
                ],
              ),
            ),
            _PushCard(
              status: pushStatus,
              busy: busy,
              onEnable: onEnablePush,
              onDisable: onDisablePush,
              onPreview: onPreviewPush,
            ),
          ],
        ),
        const SizedBox(height: 18),
        SectionCard(
          title: 'Ключевые разделы',
          subtitle: 'Сводка по основным государственным потокам портала.',
          child: Wrap(
            spacing: 14,
            runSpacing: 14,
            children: [
              MetricPill(
                title: 'Ratubles',
                value: '${profile?['ratubles'] ?? 0}',
                icon: Icons.savings_rounded,
                color: sky,
              ),
              MetricPill(
                title: 'Законы',
                value: '${laws.length}',
                icon: Icons.gavel_rounded,
                color: copper,
              ),
              MetricPill(
                title: 'Референдумы',
                value: '${referenda.length}',
                icon: Icons.how_to_vote_rounded,
                color: moss,
              ),
              MetricPill(
                title: 'Непрочитанные письма',
                value: '${unreadInboxCount(inbox)}',
                icon: Icons.mark_email_unread_rounded,
                color: lacquer,
              ),
              MetricPill(
                title: 'Законопроекты',
                value: '${bills.length}',
                icon: Icons.account_balance_rounded,
                color: brick,
              ),
            ],
          ),
        ),
        const SizedBox(height: 18),
        SectionCard(
          title: 'Последние новости',
          subtitle: 'Официальная лента портала.',
          child: news.isEmpty
              ? const EmptyStateMessage('Новостей пока нет.')
              : Column(
                  children: news
                      .take(3)
                      .map((item) => _NewsPreview(item: item))
                      .toList(),
                ),
        ),
      ],
    );
  }
}

class RatublesPage extends StatelessWidget {
  const RatublesPage({
    super.key,
    required this.loading,
    required this.busy,
    required this.profile,
    required this.users,
    required this.directory,
    required this.organizations,
    required this.transactions,
    required this.selectedRecipientKey,
    required this.transferAmountController,
    required this.transferReasonController,
    required this.onSelectedRecipientChanged,
    required this.onSendTransfer,
  });

  final bool loading;
  final bool busy;
  final JsonMap? profile;
  final List<JsonMap> users;
  final List<JsonMap> directory;
  final List<JsonMap> organizations;
  final List<JsonMap> transactions;
  final String? selectedRecipientKey;
  final TextEditingController transferAmountController;
  final TextEditingController transferReasonController;
  final ValueChanged<String?> onSelectedRecipientChanged;
  final VoidCallback onSendTransfer;

  @override
  Widget build(BuildContext context) {
    final recipients = directory
        .where((item) => item['kind'] != 'user' || item['id'] != profile?['id'])
        .toList();
    final leaderboard = [...users]
      ..sort(
        (left, right) => ((right['ratubles'] as num?)?.toInt() ?? 0).compareTo(
          (left['ratubles'] as num?)?.toInt() ?? 0,
        ),
      );
    final currentBalance = ((profile?['ratubles'] as num?)?.toInt()) ?? 0;
    final totalBalance = leaderboard.fold<int>(
      0,
      (sum, item) => sum + (((item['ratubles'] as num?)?.toInt()) ?? 0),
    );
    final orgTotalBalance = organizations.fold<int>(
      0,
      (sum, item) => sum + (((item['ratubles'] as num?)?.toInt()) ?? 0),
    );
    final highestBalance = leaderboard.isEmpty
        ? currentBalance
        : ((leaderboard.first['ratubles'] as num?)?.toInt() ?? 0);

    return PageBody(
      loading: loading,
      children: [
        AdaptivePaneGrid(
          minChildWidth: 320,
          children: [
            SectionCard(
              title: 'Кошелёк Ratubles',
              subtitle:
                  'Персональный баланс цифровой валюты Ratcraftia для гражданских и государственных операций.',
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(22),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [Color(0xFF2E1B14), Color(0xFF6B2F20)],
                  ),
                  borderRadius: BorderRadius.circular(24),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Ваш баланс',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        color: Colors.white.withValues(alpha: 0.82),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      '$currentBalance',
                      style: Theme.of(context).textTheme.displayMedium
                          ?.copyWith(
                            color: Colors.white,
                            fontWeight: FontWeight.w700,
                          ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Ratubles закреплены в вашем профиле и уже доступны во всех административных списках.',
                      style: TextStyle(
                        color: Colors.white.withValues(alpha: 0.86),
                        height: 1.45,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            SectionCard(
              title: 'Экономический срез',
              subtitle: users.isEmpty
                  ? 'Персональный режим, потому что доступ к общему реестру балансов есть только у управления.'
                  : 'Сводка по доступному реестру граждан и сотрудников.',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  InfoRow(
                    label: 'Ваш доступ',
                    value:
                        profile?['permissions_label']?.toString() ??
                        'Не указано',
                  ),
                  InfoRow(
                    label: 'Позиция',
                    value:
                        profile?['position_title']?.toString() ?? 'Не указано',
                  ),
                  InfoRow(label: 'Максимум', value: '$highestBalance'),
                  if (users.isNotEmpty)
                    InfoRow(label: 'Сумма в реестре', value: '$totalBalance'),
                  if (organizations.isNotEmpty)
                    InfoRow(
                      label: 'Баланс организаций',
                      value: '$orgTotalBalance',
                    ),
                ],
              ),
            ),
            SectionCard(
              title: 'Перевод Ratubles',
              subtitle:
                  'Перевод отправляется с вашего баланса и сохраняется в истории вместе с причиной.',
              child: recipients.isEmpty
                  ? const EmptyStateMessage(
                      'Для перевода пока нет доступных получателей.',
                    )
                  : Column(
                      children: [
                        DropdownButtonFormField<String>(
                          initialValue: selectedRecipientKey,
                          items: recipients
                              .map(
                                (target) => DropdownMenuItem<String>(
                                  value: '${target['kind']}:${target['id']}',
                                  child: Text(
                                    '${target['full_name']} · ${target['code']}',
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                              )
                              .toList(),
                          onChanged: onSelectedRecipientChanged,
                          decoration: const InputDecoration(
                            labelText: 'Получатель',
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'В список включены граждане и организации RGOV.',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                        const SizedBox(height: 14),
                        TextField(
                          controller: transferAmountController,
                          keyboardType: TextInputType.number,
                          decoration: const InputDecoration(
                            labelText: 'Сумма',
                            hintText: 'Например: 125',
                          ),
                        ),
                        const SizedBox(height: 14),
                        TextField(
                          controller: transferReasonController,
                          minLines: 2,
                          maxLines: 4,
                          decoration: const InputDecoration(
                            labelText: 'Причина перевода',
                          ),
                        ),
                        const SizedBox(height: 14),
                        FilledButton(
                          onPressed: busy ? null : onSendTransfer,
                          child: const Text('Отправить Ratubles'),
                        ),
                      ],
                    ),
            ),
          ],
        ),
        const SizedBox(height: 18),
        SectionCard(
          title: 'История операций',
          subtitle:
              'Все входящие и исходящие движения с указанием причины и времени.',
          child: transactions.isEmpty
              ? const EmptyStateMessage('Транзакций пока нет.')
              : Column(
                  children: transactions
                      .map(
                        (transaction) =>
                            _RatublesTransactionTile(transaction: transaction),
                      )
                      .toList(),
                ),
        ),
        const SizedBox(height: 18),
        SectionCard(
          title: 'Лидерборд Ratubles',
          subtitle: users.isEmpty
              ? 'Сейчас доступен только ваш персональный баланс.'
              : 'Баланс отсортирован по убыванию для быстрого просмотра управлением.',
          child: users.isEmpty
              ? const EmptyStateMessage(
                  'Общий рейтинг недоступен для текущего набора прав. Ваш баланс всё равно отображается в верхней карточке.',
                )
              : Column(
                  children: leaderboard
                      .take(12)
                      .map((item) => _RatublesLeaderTile(user: item))
                      .toList(),
                ),
        ),
      ],
    );
  }
}

class MailPage extends StatelessWidget {
  const MailPage({
    super.key,
    required this.loading,
    required this.busy,
    required this.mailToController,
    required this.mailSubjectController,
    required this.mailTextController,
    required this.inbox,
    required this.sent,
    required this.onSendMail,
  });

  final bool loading;
  final bool busy;
  final TextEditingController mailToController;
  final TextEditingController mailSubjectController;
  final TextEditingController mailTextController;
  final List<JsonMap> inbox;
  final List<JsonMap> sent;
  final VoidCallback onSendMail;

  @override
  Widget build(BuildContext context) {
    return PageBody(
      loading: loading,
      children: [
        SectionCard(
          title: 'GovMail',
          subtitle:
              'Поддерживаются адреса вида UIN@citizen, NAA.parlament@gov и login@fn.',
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              TextField(
                controller: mailToController,
                decoration: const InputDecoration(
                  labelText: 'Кому',
                  hintText: '1.26.563372@citizen или NAA.parlament@gov',
                ),
              ),
              const SizedBox(height: 14),
              TextField(
                controller: mailSubjectController,
                decoration: const InputDecoration(labelText: 'Тема'),
              ),
              const SizedBox(height: 14),
              TextField(
                controller: mailTextController,
                minLines: 5,
                maxLines: 8,
                decoration: const InputDecoration(labelText: 'Текст'),
              ),
              const SizedBox(height: 14),
              FilledButton(
                onPressed: busy ? null : onSendMail,
                child: const Text('Отправить письмо'),
              ),
            ],
          ),
        ),
        const SizedBox(height: 18),
        AdaptivePaneGrid(
          minChildWidth: 420,
          children: [
            SectionCard(
              title: 'Входящие',
              subtitle: 'Письма, пришедшие в ваш GovMail.',
              child: _MessageList(messages: inbox, incoming: true),
            ),
            SectionCard(
              title: 'Отправленные',
              subtitle: 'История исходящей переписки.',
              child: _MessageList(messages: sent, incoming: false),
            ),
          ],
        ),
      ],
    );
  }
}

class LawsPage extends StatelessWidget {
  const LawsPage({super.key, required this.loading, required this.laws});

  final bool loading;
  final List<JsonMap> laws;

  @override
  Widget build(BuildContext context) {
    return PageBody(
      loading: loading,
      children: [
        SectionCard(
          title: 'Законы и конституция',
          subtitle:
              'В реестре отражаются действующие версии нормативных актов.',
          child: laws.isEmpty
              ? const EmptyStateMessage('Законы пока не опубликованы.')
              : Column(
                  children: laws.map((law) => _LawCard(law: law)).toList(),
                ),
        ),
      ],
    );
  }
}

class ReferendaPage extends StatelessWidget {
  const ReferendaPage({
    super.key,
    required this.loading,
    required this.busy,
    required this.canCreateReferenda,
    required this.referendumTitleController,
    required this.referendumDescriptionController,
    required this.referendumTextController,
    required this.referendumLawIdController,
    required this.referendumSubjectController,
    required this.referendumTargetLevel,
    required this.referendumMatterType,
    required this.onTargetLevelChanged,
    required this.onMatterTypeChanged,
    required this.onCreateReferendum,
    required this.referenda,
    required this.onSignReferendum,
    required this.onVoteReferendum,
    required this.onPublishReferendum,
  });

  final bool loading;
  final bool busy;
  final bool canCreateReferenda;
  final TextEditingController referendumTitleController;
  final TextEditingController referendumDescriptionController;
  final TextEditingController referendumTextController;
  final TextEditingController referendumLawIdController;
  final TextEditingController referendumSubjectController;
  final String referendumTargetLevel;
  final String referendumMatterType;
  final ValueChanged<String?> onTargetLevelChanged;
  final ValueChanged<String?> onMatterTypeChanged;
  final VoidCallback onCreateReferendum;
  final List<JsonMap> referenda;
  final ValueChanged<int> onSignReferendum;
  final void Function(int id, String vote) onVoteReferendum;
  final ValueChanged<int> onPublishReferendum;

  @override
  Widget build(BuildContext context) {
    return PageBody(
      loading: loading,
      children: [
        if (canCreateReferenda) ...[
          SectionCard(
            title: 'Новый референдум',
            subtitle:
                'Сначала собираются подписи, затем голосование длится 4 дня и требует кворума 1/3 граждан.',
            child: Column(
              children: [
                TextField(
                  controller: referendumTitleController,
                  decoration: const InputDecoration(labelText: 'Заголовок'),
                ),
                const SizedBox(height: 14),
                TextField(
                  controller: referendumDescriptionController,
                  decoration: const InputDecoration(
                    labelText: 'Краткое описание',
                  ),
                ),
                const SizedBox(height: 14),
                DropdownButtonFormField<String>(
                  initialValue: referendumMatterType,
                  items: const [
                    DropdownMenuItem(
                      value: 'constitution_amendment',
                      child: Text('Поправка к конституции'),
                    ),
                    DropdownMenuItem(
                      value: 'law_change',
                      child: Text('Законодательный вопрос'),
                    ),
                    DropdownMenuItem(
                      value: 'deputy_recall',
                      child: Text('Отзыв депутата'),
                    ),
                    DropdownMenuItem(
                      value: 'official_recall',
                      child: Text('Отзыв должностного лица'),
                    ),
                    DropdownMenuItem(
                      value: 'government_question',
                      child: Text('Иной государственный вопрос'),
                    ),
                  ],
                  onChanged: onMatterTypeChanged,
                  decoration: const InputDecoration(labelText: 'Тип вопроса'),
                ),
                const SizedBox(height: 14),
                DropdownButtonFormField<String>(
                  initialValue: referendumTargetLevel,
                  items: const [
                    DropdownMenuItem(
                      value: 'constitution',
                      child: Text('Конституция'),
                    ),
                    DropdownMenuItem(value: 'law', child: Text('Закон')),
                  ],
                  onChanged: onTargetLevelChanged,
                  decoration: const InputDecoration(
                    labelText: 'Целевой уровень',
                  ),
                ),
                const SizedBox(height: 14),
                TextField(
                  controller: referendumSubjectController,
                  decoration: const InputDecoration(
                    labelText: 'Логин, УИН или УАН должностного лица',
                    hintText: 'Нужно только для отзыва',
                  ),
                ),
                const SizedBox(height: 14),
                TextField(
                  controller: referendumLawIdController,
                  decoration: const InputDecoration(
                    labelText: 'ID закона для изменения',
                    hintText: 'Необязательно',
                  ),
                ),
                const SizedBox(height: 14),
                TextField(
                  controller: referendumTextController,
                  minLines: 5,
                  maxLines: 9,
                  decoration: const InputDecoration(
                    labelText: 'Предлагаемый текст',
                  ),
                ),
                const SizedBox(height: 14),
                FilledButton(
                  onPressed: busy ? null : onCreateReferendum,
                  child: const Text('Создать референдум'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 18),
        ],
        SectionCard(
          title: 'Референдумы',
          subtitle:
              'Инициативы проходят через подписи, кворум и обязательное исполнение результата.',
          child: referenda.isEmpty
              ? const EmptyStateMessage('Референдумов пока нет.')
              : Column(
                  children: referenda
                      .map(
                        (referendum) => _ReferendumCard(
                          referendum: referendum,
                          busy: busy,
                          canSign:
                              referendum['status'] == 'collecting_signatures',
                          canVote: referendum['status'] == 'open',
                          canPublish: referendum['status'] == 'approved',
                          onSign: onSignReferendum,
                          onVote: onVoteReferendum,
                          onPublish: onPublishReferendum,
                        ),
                      )
                      .toList(),
                ),
        ),
      ],
    );
  }
}

class ParliamentPage extends StatelessWidget {
  const ParliamentPage({
    super.key,
    required this.loading,
    required this.busy,
    required this.parliamentSummary,
    required this.parliamentElections,
    required this.partyController,
    required this.onNominate,
    required this.onSignCandidate,
    required this.onVoteCandidate,
    required this.canCreateBills,
    required this.billTitleController,
    required this.billSummaryController,
    required this.billTextController,
    required this.billLawIdController,
    required this.onCreateBill,
    required this.bills,
    required this.onVoteBill,
    required this.onPublishBill,
  });

  final bool loading;
  final bool busy;
  final JsonMap? parliamentSummary;
  final List<JsonMap> parliamentElections;
  final TextEditingController partyController;
  final VoidCallback onNominate;
  final void Function(int electionId, int candidateId) onSignCandidate;
  final void Function(int electionId, int candidateId, String vote)
  onVoteCandidate;
  final bool canCreateBills;
  final TextEditingController billTitleController;
  final TextEditingController billSummaryController;
  final TextEditingController billTextController;
  final TextEditingController billLawIdController;
  final VoidCallback onCreateBill;
  final List<JsonMap> bills;
  final void Function(int id, String vote) onVoteBill;
  final ValueChanged<int> onPublishBill;

  @override
  Widget build(BuildContext context) {
    final deputies =
        parliamentSummary?['deputies'] as List<dynamic>? ?? const <dynamic>[];
    final activeElection = parliamentSummary?['active_election'] as JsonMap?;

    return PageBody(
      loading: loading,
      children: [
        SectionCard(
          title: 'Состав парламента',
          subtitle:
              'Конституционный состав фиксирован: 20 депутатов, кворум для работы не ниже 10.',
          child: parliamentSummary == null
              ? const EmptyStateMessage('Сводка по парламенту загружается.')
              : Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        Chip(
                          label: Text(
                            'Мест: ${parliamentSummary?['seat_count'] ?? 20}',
                          ),
                        ),
                        Chip(
                          label: Text(
                            'Кворум: ${parliamentSummary?['quorum'] ?? 10}',
                          ),
                        ),
                        Chip(
                          label: Text(
                            'Вакансии: ${parliamentSummary?['vacancies'] ?? 20}',
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    if (deputies.isEmpty)
                      const Text('Действующих депутатов пока нет.')
                    else
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: deputies
                            .map(
                              (item) => Chip(
                                label: Text(
                                  'Место ${(item as JsonMap)['seat_number']}: ${item['full_name']}',
                                ),
                              ),
                            )
                            .toList(),
                      ),
                  ],
                ),
        ),
        const SizedBox(height: 18),
        if (activeElection != null) ...[
          SectionCard(
            title: 'Активные выборы',
            subtitle:
                'Самовыдвижение возможно после сбора подписей, а избиратель может поддержать кандидатов на число вакантных мест.',
            child: Column(
              children: [
                TextField(
                  controller: partyController,
                  decoration: const InputDecoration(
                    labelText: 'Партия',
                    hintText: 'Оставьте пустым для самовыдвижения по подписям',
                  ),
                ),
                const SizedBox(height: 14),
                FilledButton(
                  onPressed: busy ? null : onNominate,
                  child: const Text('Выдвинуть свою кандидатуру'),
                ),
                const SizedBox(height: 18),
                ...parliamentElections.map(
                  (election) => _ParliamentElectionCard(
                    election: election,
                    busy: busy,
                    onSignCandidate: onSignCandidate,
                    onVoteCandidate: onVoteCandidate,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 18),
        ],
        if (canCreateBills) ...[
          SectionCard(
            title: 'Новый законопроект',
            subtitle:
                'Закон принимается только при кворуме и большинстве голосов действующих депутатов.',
            child: Column(
              children: [
                TextField(
                  controller: billTitleController,
                  decoration: const InputDecoration(
                    labelText: 'Название закона',
                  ),
                ),
                const SizedBox(height: 14),
                TextField(
                  controller: billSummaryController,
                  decoration: const InputDecoration(
                    labelText: 'Краткое описание',
                  ),
                ),
                const SizedBox(height: 14),
                TextField(
                  controller: billLawIdController,
                  decoration: const InputDecoration(
                    labelText: 'ID закона для изменения',
                    hintText: 'Оставьте пустым для нового закона',
                  ),
                ),
                const SizedBox(height: 14),
                TextField(
                  controller: billTextController,
                  minLines: 5,
                  maxLines: 9,
                  decoration: const InputDecoration(
                    labelText: 'Текст законопроекта',
                  ),
                ),
                const SizedBox(height: 14),
                FilledButton(
                  onPressed: busy ? null : onCreateBill,
                  child: const Text('Создать законопроект'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 18),
        ],
        SectionCard(
          title: 'Парламентская лента',
          subtitle:
              'Законопроекты учитывают конституционный кворум парламента.',
          child: bills.isEmpty
              ? const EmptyStateMessage('Законопроектов пока нет.')
              : Column(
                  children: bills
                      .map(
                        (bill) => _BillCard(
                          bill: bill,
                          busy: busy,
                          canAct: canCreateBills,
                          onVote: onVoteBill,
                          onPublish: onPublishBill,
                        ),
                      )
                      .toList(),
                ),
        ),
      ],
    );
  }
}

class NewsPage extends StatelessWidget {
  const NewsPage({
    super.key,
    required this.loading,
    required this.busy,
    required this.canPostNews,
    required this.newsTitleController,
    required this.newsBodyController,
    required this.news,
    required this.onPostNews,
    required this.onDeleteNews,
  });

  final bool loading;
  final bool busy;
  final bool canPostNews;
  final TextEditingController newsTitleController;
  final TextEditingController newsBodyController;
  final List<JsonMap> news;
  final VoidCallback onPostNews;
  final ValueChanged<int> onDeleteNews;

  @override
  Widget build(BuildContext context) {
    return PageBody(
      loading: loading,
      children: [
        if (canPostNews) ...[
          SectionCard(
            title: 'Публикация новости',
            subtitle:
                'Раздел для исполнительной власти и уполномоченных сотрудников.',
            child: Column(
              children: [
                TextField(
                  controller: newsTitleController,
                  decoration: const InputDecoration(labelText: 'Заголовок'),
                ),
                const SizedBox(height: 14),
                TextField(
                  controller: newsBodyController,
                  minLines: 4,
                  maxLines: 7,
                  decoration: const InputDecoration(labelText: 'Текст новости'),
                ),
                const SizedBox(height: 14),
                FilledButton(
                  onPressed: busy ? null : onPostNews,
                  child: const Text('Опубликовать'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 18),
        ],
        SectionCard(
          title: 'Новости Ratcraftia',
          subtitle: 'Официальная лента портала.',
          child: news.isEmpty
              ? const EmptyStateMessage('Новостей пока нет.')
              : Column(
                  children: news
                      .map(
                        (item) => _NewsCard(
                          item: item,
                          canDelete: canPostNews,
                          busy: busy,
                          onDelete: onDeleteNews,
                        ),
                      )
                      .toList(),
                ),
        ),
      ],
    );
  }
}

class AdminPage extends StatelessWidget {
  const AdminPage({
    super.key,
    required this.loading,
    required this.busy,
    required this.canOpenAdmin,
    required this.canCreateOrganizations,
    required this.canManagePersonnel,
    required this.canCreateUsers,
    required this.canUpdateUsers,
    required this.canManagePermissions,
    required this.canMintRatubles,
    required this.canReadAdminLogs,
    required this.canReadExternalAuthApps,
    required this.canApproveExternalAuthApps,
    required this.users,
    required this.organizations,
    required this.ledger,
    required this.adminLogs,
    required this.externalAuthApps,
    required this.selectedUserId,
    required this.selectedMintTargetKey,
    required this.selectedOrganizationSlug,
    required this.orgNameController,
    required this.orgSlugController,
    required this.orgDescriptionController,
    required this.userUinController,
    required this.userUanController,
    required this.userLoginController,
    required this.userPasswordController,
    required this.userFirstNameController,
    required this.userLastNameController,
    required this.userPatronymicController,
    required this.userPermissionsController,
    required this.userPositionController,
    required this.assignedPermissionsController,
    required this.personnelPositionController,
    required this.userEditUinController,
    required this.userEditUanController,
    required this.userEditFirstNameController,
    required this.userEditLastNameController,
    required this.userEditPatronymicController,
    required this.mintAmountController,
    required this.mintReasonController,
    required this.onSelectedUserChanged,
    required this.onSelectedMintTargetChanged,
    required this.onSelectedOrganizationChanged,
    required this.onCreateOrganization,
    required this.onHireSelectedUser,
    required this.onFireSelectedUser,
    required this.onChangePermissionsForSelectedUser,
    required this.onCreateUser,
    required this.onUpdateSelectedUser,
    required this.onMintRatubles,
    required this.onApproveExternalAuthApp,
    required this.onDeactivateExternalAuthApp,
  });

  final bool loading;
  final bool busy;
  final bool canOpenAdmin;
  final bool canCreateOrganizations;
  final bool canManagePersonnel;
  final bool canCreateUsers;
  final bool canUpdateUsers;
  final bool canManagePermissions;
  final bool canMintRatubles;
  final bool canReadAdminLogs;
  final bool canReadExternalAuthApps;
  final bool canApproveExternalAuthApps;
  final List<JsonMap> users;
  final List<JsonMap> organizations;
  final List<JsonMap> ledger;
  final List<JsonMap> adminLogs;
  final List<JsonMap> externalAuthApps;
  final int? selectedUserId;
  final String? selectedMintTargetKey;
  final String? selectedOrganizationSlug;
  final TextEditingController orgNameController;
  final TextEditingController orgSlugController;
  final TextEditingController orgDescriptionController;
  final TextEditingController userUinController;
  final TextEditingController userUanController;
  final TextEditingController userLoginController;
  final TextEditingController userPasswordController;
  final TextEditingController userFirstNameController;
  final TextEditingController userLastNameController;
  final TextEditingController userPatronymicController;
  final TextEditingController userPermissionsController;
  final TextEditingController userPositionController;
  final TextEditingController assignedPermissionsController;
  final TextEditingController personnelPositionController;
  final TextEditingController userEditUinController;
  final TextEditingController userEditUanController;
  final TextEditingController userEditFirstNameController;
  final TextEditingController userEditLastNameController;
  final TextEditingController userEditPatronymicController;
  final TextEditingController mintAmountController;
  final TextEditingController mintReasonController;
  final ValueChanged<int?> onSelectedUserChanged;
  final ValueChanged<String?> onSelectedMintTargetChanged;
  final ValueChanged<String?> onSelectedOrganizationChanged;
  final VoidCallback onCreateOrganization;
  final VoidCallback onHireSelectedUser;
  final VoidCallback onFireSelectedUser;
  final VoidCallback onChangePermissionsForSelectedUser;
  final VoidCallback onCreateUser;
  final VoidCallback onUpdateSelectedUser;
  final VoidCallback onMintRatubles;
  final ValueChanged<int> onApproveExternalAuthApp;
  final ValueChanged<int> onDeactivateExternalAuthApp;

  @override
  Widget build(BuildContext context) {
    if (!canOpenAdmin) {
      return PageBody(
        loading: loading,
        children: const [
          SectionCard(
            title: 'Управление',
            subtitle:
                'Этот раздел доступен только пользователям с административными правами.',
            child: EmptyStateMessage(
              'Для реестра, кадровых операций и настройки прав нужны соответствующие permission-записи.',
            ),
          ),
        ],
      );
    }

    final userItems = users
        .map(
          (user) => DropdownMenuItem<int>(
            value: user['id'] as int,
            child: Text(
              '${user['full_name']} (${user['login']})',
              overflow: TextOverflow.ellipsis,
            ),
          ),
        )
        .toList();
    final organizationItems = organizations
        .map(
          (organization) => DropdownMenuItem<String>(
            value: organization['slug'] as String,
            child: Text(organization['name'].toString()),
          ),
        )
        .toList();
    final mintTargetItems = [
      ...users.map(
        (user) => DropdownMenuItem<String>(
          value: 'user:${user['id']}',
          child: Text(
            '${user['full_name']} (${user['login']})',
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ),
      ...organizations.map(
        (organization) => DropdownMenuItem<String>(
          value: 'organization:${organization['id']}',
          child: Text(
            '${organization['name']} (${organization['slug']})',
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ),
    ];

    return PageBody(
      loading: loading,
      children: [
        AdaptivePaneGrid(
          minChildWidth: 360,
          children: [
            if (canCreateOrganizations)
              SectionCard(
                title: 'Организации',
                subtitle: 'Создание новых органов и структур.',
                child: Column(
                  children: [
                    TextField(
                      controller: orgNameController,
                      decoration: const InputDecoration(labelText: 'Название'),
                    ),
                    const SizedBox(height: 14),
                    TextField(
                      controller: orgSlugController,
                      decoration: const InputDecoration(labelText: 'Slug'),
                    ),
                    const SizedBox(height: 14),
                    TextField(
                      controller: orgDescriptionController,
                      minLines: 3,
                      maxLines: 5,
                      decoration: const InputDecoration(labelText: 'Описание'),
                    ),
                    const SizedBox(height: 14),
                    FilledButton(
                      onPressed: busy ? null : onCreateOrganization,
                      child: const Text('Создать организацию'),
                    ),
                  ],
                ),
              ),
            if (organizations.isNotEmpty)
              SectionCard(
                title: 'Баланс организаций',
                subtitle:
                    'Каждая организация теперь может хранить собственные Ratubles на отдельном балансе.',
                child: Column(
                  children: organizations
                      .map(
                        (organization) => _OrganizationBalanceTile(
                          organization: organization,
                        ),
                      )
                      .toList(),
                ),
              ),
            if (canManagePersonnel)
              SectionCard(
                title: 'Кадровые операции',
                subtitle: 'Приём на работу, увольнение и назначение в орган.',
                child: Column(
                  children: [
                    DropdownButtonFormField<int>(
                      initialValue: selectedUserId,
                      items: userItems,
                      onChanged: onSelectedUserChanged,
                      decoration: const InputDecoration(
                        labelText: 'Пользователь',
                      ),
                    ),
                    const SizedBox(height: 14),
                    DropdownButtonFormField<String>(
                      initialValue: selectedOrganizationSlug,
                      items: organizationItems,
                      onChanged: onSelectedOrganizationChanged,
                      decoration: const InputDecoration(
                        labelText: 'Организация',
                      ),
                    ),
                    const SizedBox(height: 14),
                    TextField(
                      controller: personnelPositionController,
                      decoration: const InputDecoration(labelText: 'Должность'),
                    ),
                    const SizedBox(height: 14),
                    Wrap(
                      spacing: 10,
                      runSpacing: 10,
                      children: [
                        FilledButton.tonal(
                          onPressed: busy ? null : onHireSelectedUser,
                          child: const Text('Назначить'),
                        ),
                        OutlinedButton(
                          onPressed: busy ? null : onFireSelectedUser,
                          child: const Text('Уволить'),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            if (canManagePermissions)
              SectionCard(
                title: 'Права доступа',
                subtitle:
                    'Изменение permission-списка пользователя. Используйте `*` для полного доступа.',
                child: Column(
                  children: [
                    DropdownButtonFormField<int>(
                      initialValue: selectedUserId,
                      items: userItems,
                      onChanged: onSelectedUserChanged,
                      decoration: const InputDecoration(
                        labelText: 'Пользователь',
                      ),
                    ),
                    const SizedBox(height: 14),
                    TextField(
                      controller: assignedPermissionsController,
                      minLines: 2,
                      maxLines: 4,
                      decoration: const InputDecoration(
                        labelText: 'Permissions',
                        hintText:
                            'Например: news.manage, referenda.manage или *',
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Список разделяется запятыми. Пустое поле снимет все специальные права.',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    const SizedBox(height: 14),
                    FilledButton.tonal(
                      onPressed: busy
                          ? null
                          : onChangePermissionsForSelectedUser,
                      child: const Text('Сохранить права'),
                    ),
                  ],
                ),
              ),
            if (canUpdateUsers)
              SectionCard(
                title: 'Редактирование пользователя',
                subtitle:
                    'Обновление ФИО, УИН и УАН для выбранной записи реестра.',
                child: Column(
                  children: [
                    DropdownButtonFormField<int>(
                      initialValue: selectedUserId,
                      items: userItems,
                      onChanged: onSelectedUserChanged,
                      decoration: const InputDecoration(
                        labelText: 'Пользователь',
                      ),
                    ),
                    const SizedBox(height: 14),
                    AdaptivePaneGrid(
                      minChildWidth: 180,
                      spacing: 12,
                      children: [
                        TextField(
                          controller: userEditFirstNameController,
                          decoration: const InputDecoration(labelText: 'Имя'),
                        ),
                        TextField(
                          controller: userEditLastNameController,
                          decoration: const InputDecoration(
                            labelText: 'Фамилия',
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),
                    TextField(
                      controller: userEditPatronymicController,
                      decoration: const InputDecoration(labelText: 'Отчество'),
                    ),
                    const SizedBox(height: 14),
                    AdaptivePaneGrid(
                      minChildWidth: 180,
                      spacing: 12,
                      children: [
                        TextField(
                          controller: userEditUinController,
                          decoration: const InputDecoration(labelText: 'УИН'),
                        ),
                        TextField(
                          controller: userEditUanController,
                          decoration: const InputDecoration(labelText: 'УАН'),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),
                    FilledButton.tonal(
                      onPressed: busy ? null : onUpdateSelectedUser,
                      child: const Text('Сохранить данные'),
                    ),
                  ],
                ),
              ),
            if (canCreateUsers)
              SectionCard(
                title: 'Создание пользователя',
                subtitle:
                    'Создайте гражданина или сотрудника и задайте права доступа напрямую.',
                child: Column(
                  children: [
                    TextField(
                      controller: userUinController,
                      decoration: const InputDecoration(labelText: 'УИН'),
                    ),
                    const SizedBox(height: 14),
                    TextField(
                      controller: userUanController,
                      decoration: const InputDecoration(labelText: 'УАН'),
                    ),
                    const SizedBox(height: 14),
                    TextField(
                      controller: userLoginController,
                      decoration: const InputDecoration(labelText: 'Логин'),
                    ),
                    const SizedBox(height: 14),
                    TextField(
                      controller: userPasswordController,
                      obscureText: true,
                      decoration: const InputDecoration(labelText: 'Пароль'),
                    ),
                    const SizedBox(height: 14),
                    AdaptivePaneGrid(
                      minChildWidth: 180,
                      spacing: 12,
                      children: [
                        TextField(
                          controller: userFirstNameController,
                          decoration: const InputDecoration(labelText: 'Имя'),
                        ),
                        TextField(
                          controller: userLastNameController,
                          decoration: const InputDecoration(
                            labelText: 'Фамилия',
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),
                    TextField(
                      controller: userPatronymicController,
                      decoration: const InputDecoration(labelText: 'Отчество'),
                    ),
                    const SizedBox(height: 14),
                    TextField(
                      controller: userPermissionsController,
                      minLines: 2,
                      maxLines: 4,
                      decoration: const InputDecoration(
                        labelText: 'Permissions',
                        hintText:
                            'Например: bills.manage, referenda.manage или оставьте пустым',
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Для полного доступа используйте `*`. Без списка пользователь останется с базовым доступом.',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    const SizedBox(height: 14),
                    TextField(
                      controller: userPositionController,
                      decoration: const InputDecoration(labelText: 'Должность'),
                    ),
                    const SizedBox(height: 14),
                    FilledButton(
                      onPressed: busy ? null : onCreateUser,
                      child: const Text('Создать пользователя'),
                    ),
                  ],
                ),
              ),
            if (canMintRatubles)
              SectionCard(
                title: 'Эмиссия Ratubles',
                subtitle:
                    'Администратор может начислить сумму как пользователю, так и организации с обязательной причиной.',
                child: Column(
                  children: [
                    DropdownButtonFormField<String>(
                      initialValue: selectedMintTargetKey,
                      items: mintTargetItems,
                      onChanged: onSelectedMintTargetChanged,
                      decoration: const InputDecoration(
                        labelText: 'Получатель',
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Начисление сразу попадает в общий ledger Ratubles.',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    const SizedBox(height: 14),
                    TextField(
                      controller: mintAmountController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(labelText: 'Сумма'),
                    ),
                    const SizedBox(height: 14),
                    TextField(
                      controller: mintReasonController,
                      minLines: 2,
                      maxLines: 4,
                      decoration: const InputDecoration(
                        labelText: 'Причина начисления',
                      ),
                    ),
                    const SizedBox(height: 14),
                    FilledButton(
                      onPressed: busy ? null : onMintRatubles,
                      child: const Text('Начислить Ratubles'),
                    ),
                  ],
                ),
              ),
            if (canReadExternalAuthApps)
              SectionCard(
                title: 'Внешняя авторизация',
                subtitle:
                    'Сторонние приложения используют OAuth 2.0 redirect/consent flow и получают токены только после одобрения администратором.',
                child: externalAuthApps.isEmpty
                    ? const EmptyStateMessage(
                        'Запросов на внешнюю авторизацию пока нет.',
                      )
                    : Column(
                        children: externalAuthApps
                            .map(
                              (application) => _ExternalAuthAppTile(
                                application: application,
                                busy: busy,
                                canApprove: canApproveExternalAuthApps,
                                onApprove: () => onApproveExternalAuthApp(
                                  application['id'] as int,
                                ),
                                onDeactivate: () => onDeactivateExternalAuthApp(
                                  application['id'] as int,
                                ),
                              ),
                            )
                            .toList(),
                      ),
              ),
          ],
        ),
        if (canReadAdminLogs) ...[
          const SizedBox(height: 18),
          AdaptivePaneGrid(
            minChildWidth: 420,
            children: [
              SectionCard(
                title: 'Журнал администратора',
                subtitle: 'Последние управленческие действия и причины.',
                child: adminLogs.isEmpty
                    ? const EmptyStateMessage('Журнал пока пуст.')
                    : Column(
                        children: adminLogs
                            .map((entry) => _AdminLogTile(entry: entry))
                            .toList(),
                      ),
              ),
              SectionCard(
                title: 'История транзакций',
                subtitle: 'Глобальная лента переводов и начислений Ratubles.',
                child: ledger.isEmpty
                    ? const EmptyStateMessage('Транзакций пока нет.')
                    : Column(
                        children: ledger
                            .map(
                              (transaction) => _RatublesTransactionTile(
                                transaction: transaction,
                              ),
                            )
                            .toList(),
                      ),
              ),
            ],
          ),
        ],
        if (users.isNotEmpty) ...[
          const SizedBox(height: 18),
          SectionCard(
            title: 'Реестр сотрудников и граждан',
            subtitle:
                'Контрольная страница показывает полный УАН, УИН, баланс и статус пользователя.',
            child: Column(
              children: users.map((user) => _UserCard(user: user)).toList(),
            ),
          ),
        ],
      ],
    );
  }
}

class _OrganizationBalanceTile extends StatelessWidget {
  const _OrganizationBalanceTile({required this.organization});

  final JsonMap organization;

  @override
  Widget build(BuildContext context) {
    final name = organization['name']?.toString() ?? 'Без названия';
    final slug = organization['slug']?.toString() ?? 'unknown';
    final description = organization['description']?.toString() ?? '';
    final ratubles = organization['ratubles']?.toString() ?? '0';

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: appInsetColor(context),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '$name · $ratubles Ratubles',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              color: appTextColor(context),
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            'Slug: $slug',
            style: TextStyle(color: appMutedTextColor(context)),
          ),
          if (description.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(
              description,
              style: TextStyle(color: appMutedTextColor(context, 0.82)),
            ),
          ],
        ],
      ),
    );
  }
}

class _ExternalAuthAppTile extends StatelessWidget {
  const _ExternalAuthAppTile({
    required this.application,
    required this.busy,
    required this.canApprove,
    required this.onApprove,
    required this.onDeactivate,
  });

  final JsonMap application;
  final bool busy;
  final bool canApprove;
  final VoidCallback onApprove;
  final VoidCallback onDeactivate;

  @override
  Widget build(BuildContext context) {
    final approved = application['is_approved'] == true;
    final active = application['is_active'] == true;
    final name = application['name']?.toString() ?? 'Без названия';
    final clientId = application['client_id']?.toString() ?? 'unknown';
    final contactEmail = application['contact_email']?.toString() ?? '';
    final homepageUrl = application['homepage_url']?.toString() ?? '';
    final redirectUri = application['redirect_uri']?.toString() ?? '';
    final approvedBy = application['approved_by_name']?.toString() ?? '';
    final lastTokenIssuedAt = application['last_token_issued_at'];

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: appInsetColor(context),
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            name,
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
              color: appTextColor(context),
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            'Client ID: $clientId',
            style: TextStyle(color: appMutedTextColor(context)),
          ),
          if (contactEmail.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(
              'Контакт: $contactEmail',
              style: TextStyle(color: appMutedTextColor(context)),
            ),
          ],
          if (homepageUrl.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(
              'Сайт: $homepageUrl',
              style: TextStyle(color: appMutedTextColor(context)),
            ),
          ],
          if (redirectUri.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(
              'Redirect URI: $redirectUri',
              style: TextStyle(color: appMutedTextColor(context)),
            ),
          ],
          const SizedBox(height: 8),
          Text(
            approved
                ? 'Статус: ${active ? 'Одобрено' : 'Отключено'}'
                : 'Статус: Ожидает одобрения',
            style: TextStyle(
              color: approved && active ? moss : brick,
              fontWeight: FontWeight.w600,
            ),
          ),
          if (approvedBy.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(
              'Одобрил: $approvedBy',
              style: TextStyle(color: appMutedTextColor(context)),
            ),
          ],
          if (lastTokenIssuedAt != null) ...[
            const SizedBox(height: 4),
            Text(
              'Последний токен: ${formatTimestamp(lastTokenIssuedAt)}',
              style: TextStyle(color: appMutedTextColor(context)),
            ),
          ],
          const SizedBox(height: 12),
          if (canApprove)
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: [
                if (!approved)
                  FilledButton.tonal(
                    onPressed: busy ? null : onApprove,
                    child: const Text('Одобрить'),
                  ),
                if (approved && active)
                  OutlinedButton(
                    onPressed: busy ? null : onDeactivate,
                    child: const Text('Отключить'),
                  ),
              ],
            ),
        ],
      ),
    );
  }
}

class _DidCard extends StatelessWidget {
  const _DidCard({required this.profile, required this.did});

  final JsonMap? profile;
  final JsonMap? did;

  @override
  Widget build(BuildContext context) {
    final aliases = ((profile?['aliases'] as List<dynamic>?) ?? [])
        .map((item) => item.toString())
        .toList();
    final token = did?['token']?.toString() ?? '';
    final photoUrl = profile?['photo_url']?.toString();

    return SectionCard(
      title: 'Digital ID',
      subtitle: 'QR-код подписан JWT-токеном и живёт 10 минут.',
      child: Container(
        padding: const EdgeInsets.all(22),
        decoration: BoxDecoration(
          gradient: isDarkTheme(context)
              ? const LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [Color(0xFF211A16), Color(0xFF342722)],
                )
              : const LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [Color(0xFFFDF8F2), Color(0xFFF0E0D1)],
                ),
          borderRadius: BorderRadius.circular(24),
          border: Border.all(
            color: (isDarkTheme(context) ? Colors.white : lacquer).withValues(
              alpha: 0.08,
            ),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            LayoutBuilder(
              builder: (context, constraints) {
                final compact = constraints.maxWidth < 420;
                final qrBlock = Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(22),
                  ),
                  child: token.isEmpty
                      ? const SizedBox(
                          width: 150,
                          height: 150,
                          child: Center(child: CircularProgressIndicator()),
                        )
                      : QrImageView(
                          data: token,
                          size: 150,
                          backgroundColor: Colors.white,
                        ),
                );

                final photoBlock = Container(
                  width: 120,
                  height: 152,
                  decoration: BoxDecoration(
                    color: isDarkTheme(context)
                        ? appSoftFillColor(context)
                        : parchmentStrong,
                    borderRadius: BorderRadius.circular(22),
                  ),
                  clipBehavior: Clip.antiAlias,
                  child: photoUrl != null && photoUrl.isNotEmpty
                      ? Image.network(
                          photoUrl,
                          fit: BoxFit.cover,
                          errorBuilder: (_, _, _) => const _PhotoFallback(),
                        )
                      : const _PhotoFallback(),
                );

                if (compact) {
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          photoBlock,
                          const SizedBox(width: 14),
                          qrBlock,
                        ],
                      ),
                    ],
                  );
                }

                return Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [photoBlock, const Spacer(), qrBlock],
                );
              },
            ),
            const SizedBox(height: 22),
            InfoRow(
              label: 'ФИО',
              value: profile?['full_name']?.toString() ?? 'Не указано',
            ),
            InfoRow(
              label: 'УИН',
              value: profile?['uin']?.toString() ?? 'Не указано',
            ),
            InfoRow(
              label: 'УАН',
              value: profile?['uan']?.toString() ?? 'Не указано',
            ),
            const SizedBox(height: 18),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: aliases
                  .map(
                    (alias) =>
                        Chip(label: Text(alias), backgroundColor: parchment),
                  )
                  .toList(),
            ),
          ],
        ),
      ),
    );
  }
}

class _HierarchyCard extends StatelessWidget {
  const _HierarchyCard();

  @override
  Widget build(BuildContext context) {
    return const SectionCard(
      title: 'Иерархия власти',
      subtitle: 'Приоритет нормативных уровней Ratcraftia.',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _HierarchyLine(
            index: 1,
            title: 'Конституция',
            description:
                'Высшая норма государства. Меняется только через референдум.',
          ),
          _HierarchyLine(
            index: 2,
            title: 'Референдум',
            description:
                'Обязателен для изменения конституции и может напрямую утверждать законы.',
          ),
          _HierarchyLine(
            index: 3,
            title: 'Парламент',
            description:
                'Создаёт и изменяет законы через голосование и публикацию.',
          ),
          _HierarchyLine(
            index: 4,
            title: 'Исполнительная власть',
            description:
                'Публикует новости, управляет организациями и кадровыми решениями.',
          ),
        ],
      ),
    );
  }
}

class _PushCard extends StatelessWidget {
  const _PushCard({
    required this.status,
    required this.busy,
    required this.onEnable,
    required this.onDisable,
    required this.onPreview,
  });

  final PushNotificationStatus status;
  final bool busy;
  final VoidCallback onEnable;
  final VoidCallback onDisable;
  final VoidCallback onPreview;

  @override
  Widget build(BuildContext context) {
    final tone = !status.supported
        ? sky
        : status.enabled
        ? moss
        : status.permission == 'denied'
        ? brick
        : copper;

    return SectionCard(
      title: 'Push-уведомления',
      subtitle:
          'GovMail, новости и новые государственные события можно получать даже без открытого таба.',
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: tone.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                CircleAvatar(
                  backgroundColor: tone,
                  foregroundColor: Colors.white,
                  child: Icon(
                    status.enabled
                        ? Icons.notifications_active_rounded
                        : Icons.notifications_none_rounded,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        status.enabled
                            ? 'Уведомления активны'
                            : 'Уведомления пока не активированы',
                        style: const TextStyle(
                          color: lacquer,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        status.message,
                        style: TextStyle(
                          color: lacquer.withValues(alpha: 0.8),
                          height: 1.45,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
          Wrap(
            spacing: 10,
            runSpacing: 10,
            children: [
              FilledButton(
                onPressed: busy ? null : onEnable,
                child: const Text('Включить'),
              ),
              FilledButton.tonal(
                onPressed: busy || !status.enabled ? null : onPreview,
                child: const Text('Тест'),
              ),
              OutlinedButton(
                onPressed: busy || !status.supported ? null : onDisable,
                child: const Text('Отключить'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _PhotoFallback extends StatelessWidget {
  const _PhotoFallback();

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Icon(
          Icons.account_circle_rounded,
          size: 64,
          color: lacquer.withValues(alpha: 0.7),
        ),
        const SizedBox(height: 8),
        Text('Фото', style: TextStyle(color: lacquer.withValues(alpha: 0.75))),
      ],
    );
  }
}

class _HierarchyLine extends StatelessWidget {
  const _HierarchyLine({
    required this.index,
    required this.title,
    required this.description,
  });

  final int index;
  final String title;
  final String description;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          CircleAvatar(
            radius: 16,
            backgroundColor: copper,
            foregroundColor: Colors.white,
            child: Text('$index'),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    color: lacquer,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 4),
                Text(description),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _NewsPreview extends StatelessWidget {
  const _NewsPreview({required this.item});

  final JsonMap item;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: parchment,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              item['title'].toString(),
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                color: lacquer,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              '${item['author_name']} · ${formatTimestamp(item['created_at'])}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 10),
            Text(item['body'].toString()),
          ],
        ),
      ),
    );
  }
}

class _MessageList extends StatelessWidget {
  const _MessageList({required this.messages, required this.incoming});

  final List<JsonMap> messages;
  final bool incoming;

  @override
  Widget build(BuildContext context) {
    if (messages.isEmpty) {
      return const EmptyStateMessage('Писем пока нет.');
    }

    return Column(
      children: messages
          .map(
            (message) => Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: parchment,
                  borderRadius: BorderRadius.circular(18),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      message['subject'].toString(),
                      style: const TextStyle(
                        color: lacquer,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      incoming
                          ? 'От: ${message['from_address']}'
                          : 'Кому: ${message['to_address']}',
                      style: TextStyle(color: lacquer.withValues(alpha: 0.72)),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      '${incoming ? message['sender_name'] : message['recipient_name']} · ${formatTimestamp(message['created_at'])}',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    const SizedBox(height: 10),
                    Text(message['text'].toString()),
                  ],
                ),
              ),
            ),
          )
          .toList(),
    );
  }
}

class _LawCard extends StatelessWidget {
  const _LawCard({required this.law});

  final JsonMap law;

  @override
  Widget build(BuildContext context) {
    final level = switch (law['level'].toString()) {
      'constitution' => 'Конституция',
      'resolution' => 'Резолюция',
      _ => 'Закон',
    };
    final via = switch (law['adopted_via'].toString()) {
      'referendum' => 'референдум',
      'parliament' => 'парламент',
      _ => 'bootstrap',
    };

    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: parchment,
          borderRadius: BorderRadius.circular(22),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Wrap(
              alignment: WrapAlignment.spaceBetween,
              spacing: 8,
              runSpacing: 8,
              children: [
                Text(
                  law['title'].toString(),
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    color: lacquer,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                Chip(
                  label: Text('$level · v${law['version']}'),
                  backgroundColor: law['level'] == 'constitution'
                      ? brick.withValues(alpha: 0.12)
                      : moss.withValues(alpha: 0.12),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Принят через: $via · обновлён ${formatTimestamp(law['updated_at'])}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 12),
            SelectableText(
              law['current_text'].toString(),
              style: const TextStyle(height: 1.5),
            ),
          ],
        ),
      ),
    );
  }
}

class _ParliamentElectionCard extends StatelessWidget {
  const _ParliamentElectionCard({
    required this.election,
    required this.busy,
    required this.onSignCandidate,
    required this.onVoteCandidate,
  });

  final JsonMap election;
  final bool busy;
  final void Function(int electionId, int candidateId) onSignCandidate;
  final void Function(int electionId, int candidateId, String vote)
  onVoteCandidate;

  @override
  Widget build(BuildContext context) {
    final electionId = election['id'] as int;
    final candidates =
        election['candidates'] as List<dynamic>? ?? const <dynamic>[];

    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: parchment,
          borderRadius: BorderRadius.circular(22),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              election['title'].toString(),
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                color: lacquer,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              'Статус: ${election['status']} · мест: ${election['seat_count']} · бюллетеней: ${election['total_ballots']}',
            ),
            const SizedBox(height: 4),
            Text('Закрытие: ${formatTimestamp(election['closes_at'])}'),
            const SizedBox(height: 12),
            if (candidates.isEmpty)
              const Text('Кандидатов пока нет.')
            else
              Column(
                children: candidates.map((item) {
                  final candidate = item as JsonMap;
                  final candidateId = candidate['id'] as int;
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 10),
                    child: Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: parchmentStrong.withValues(alpha: 0.45),
                        borderRadius: BorderRadius.circular(18),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            candidate['full_name'].toString(),
                            style: const TextStyle(
                              color: lacquer,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                          if (candidate['party_name'] != null &&
                              candidate['party_name']
                                  .toString()
                                  .isNotEmpty) ...[
                            const SizedBox(height: 4),
                            Text(candidate['party_name'].toString()),
                          ],
                          const SizedBox(height: 8),
                          Wrap(
                            spacing: 8,
                            runSpacing: 8,
                            children: [
                              Chip(
                                label: Text(
                                  'Подписи: ${candidate['signatures']}/${candidate['required_signatures']}',
                                ),
                              ),
                              Chip(
                                label: Text('Голоса: ${candidate['votes']}'),
                              ),
                              Chip(
                                label: Text('Статус: ${candidate['status']}'),
                              ),
                            ],
                          ),
                          if (election['status'] == 'open') ...[
                            const SizedBox(height: 10),
                            Wrap(
                              spacing: 10,
                              runSpacing: 10,
                              children: [
                                if (candidate['status'] ==
                                    'collecting_signatures')
                                  FilledButton.tonal(
                                    onPressed: busy
                                        ? null
                                        : () => onSignCandidate(
                                            electionId,
                                            candidateId,
                                          ),
                                    child: const Text('Подписать'),
                                  ),
                                if (candidate['status'] == 'registered') ...[
                                  FilledButton.tonal(
                                    onPressed: busy
                                        ? null
                                        : () => onVoteCandidate(
                                            electionId,
                                            candidateId,
                                            'yes',
                                          ),
                                    child: const Text('В бюллетень'),
                                  ),
                                  OutlinedButton(
                                    onPressed: busy
                                        ? null
                                        : () => onVoteCandidate(
                                            electionId,
                                            candidateId,
                                            'no',
                                          ),
                                    child: const Text('Убрать'),
                                  ),
                                ],
                              ],
                            ),
                          ],
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ),
          ],
        ),
      ),
    );
  }
}

class _ReferendumCard extends StatelessWidget {
  const _ReferendumCard({
    required this.referendum,
    required this.busy,
    required this.canSign,
    required this.canVote,
    required this.canPublish,
    required this.onSign,
    required this.onVote,
    required this.onPublish,
  });

  final JsonMap referendum;
  final bool busy;
  final bool canSign;
  final bool canVote;
  final bool canPublish;
  final ValueChanged<int> onSign;
  final void Function(int id, String vote) onVote;
  final ValueChanged<int> onPublish;

  @override
  Widget build(BuildContext context) {
    final kind = switch (referendum['matter_type'].toString()) {
      'constitution_amendment' => 'Поправка к конституции',
      'deputy_recall' => 'Отзыв депутата',
      'official_recall' => 'Отзыв должностного лица',
      'government_question' => 'Государственный вопрос',
      _ => 'Законодательный референдум',
    };
    final timeline = referendum['status'] == 'collecting_signatures'
        ? 'сбор подписей'
        : formatTimestamp(referendum['closes_at']);

    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: parchment,
          borderRadius: BorderRadius.circular(22),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              referendum['title'].toString(),
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                color: lacquer,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 6),
            Text('$kind · ${referendum['proposer_name']} · $timeline'),
            if (referendum['subject_name'] != null) ...[
              const SizedBox(height: 4),
              Text('Объект вопроса: ${referendum['subject_name']}'),
            ],
            const SizedBox(height: 10),
            if (referendum['description'] != null &&
                referendum['description'].toString().isNotEmpty) ...[
              Text(
                referendum['description'].toString(),
                style: TextStyle(color: lacquer.withValues(alpha: 0.8)),
              ),
              const SizedBox(height: 10),
            ],
            SelectableText(referendum['proposed_text'].toString()),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                Chip(label: Text('Статус: ${referendum['status']}')),
                Chip(
                  label: Text(
                    'Подписи: ${referendum['signature_count']}/${referendum['required_signatures']}',
                  ),
                ),
                Chip(label: Text('За: ${referendum['yes_votes']}')),
                Chip(label: Text('Против: ${referendum['no_votes']}')),
                Chip(
                  label: Text(
                    'Кворум: ${referendum['total_votes']}/${referendum['required_quorum']}',
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: [
                if (canSign)
                  FilledButton.tonal(
                    onPressed: busy
                        ? null
                        : () => onSign(referendum['id'] as int),
                    child: const Text('Подписать инициативу'),
                  ),
                if (canVote) ...[
                  FilledButton.tonal(
                    onPressed: busy
                        ? null
                        : () => onVote(referendum['id'] as int, 'yes'),
                    child: const Text('Голосовать за'),
                  ),
                  OutlinedButton(
                    onPressed: busy
                        ? null
                        : () => onVote(referendum['id'] as int, 'no'),
                    child: const Text('Голосовать против'),
                  ),
                ],
                if (canPublish)
                  FilledButton(
                    onPressed: busy
                        ? null
                        : () => onPublish(referendum['id'] as int),
                    child: const Text('Опубликовать итог'),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _BillCard extends StatelessWidget {
  const _BillCard({
    required this.bill,
    required this.busy,
    required this.canAct,
    required this.onVote,
    required this.onPublish,
  });

  final JsonMap bill;
  final bool busy;
  final bool canAct;
  final void Function(int id, String vote) onVote;
  final ValueChanged<int> onPublish;

  @override
  Widget build(BuildContext context) {
    final canPublish = canAct && bill['status'] == 'approved';

    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: parchment,
          borderRadius: BorderRadius.circular(22),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              bill['title'].toString(),
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                color: lacquer,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              '${bill['proposer_name']} · ${formatTimestamp(bill['created_at'])}',
            ),
            if (bill['summary'] != null &&
                bill['summary'].toString().isNotEmpty) ...[
              const SizedBox(height: 10),
              Text(bill['summary'].toString()),
            ],
            const SizedBox(height: 10),
            SelectableText(bill['proposed_text'].toString()),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                Chip(label: Text('Статус: ${bill['status']}')),
                Chip(label: Text('За: ${bill['yes_votes']}')),
                Chip(label: Text('Против: ${bill['no_votes']}')),
                Chip(
                  label: Text(
                    'Кворум: ${bill['total_votes']}/${bill['quorum_required']}',
                  ),
                ),
              ],
            ),
            if (canAct) ...[
              const SizedBox(height: 12),
              Wrap(
                spacing: 10,
                runSpacing: 10,
                children: [
                  FilledButton.tonal(
                    onPressed: busy
                        ? null
                        : () => onVote(bill['id'] as int, 'yes'),
                    child: const Text('Голосовать за'),
                  ),
                  OutlinedButton(
                    onPressed: busy
                        ? null
                        : () => onVote(bill['id'] as int, 'no'),
                    child: const Text('Голосовать против'),
                  ),
                  if (canPublish)
                    FilledButton(
                      onPressed: busy
                          ? null
                          : () => onPublish(bill['id'] as int),
                      child: const Text('Опубликовать закон'),
                    ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _NewsCard extends StatelessWidget {
  const _NewsCard({
    required this.item,
    required this.canDelete,
    required this.busy,
    required this.onDelete,
  });

  final JsonMap item;
  final bool canDelete;
  final bool busy;
  final ValueChanged<int> onDelete;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Container(
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          color: parchment,
          borderRadius: BorderRadius.circular(22),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        item['title'].toString(),
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          color: lacquer,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        '${item['author_name']} · ${formatTimestamp(item['created_at'])}',
                      ),
                    ],
                  ),
                ),
                if (canDelete)
                  IconButton(
                    onPressed: busy ? null : () => onDelete(item['id'] as int),
                    icon: const Icon(Icons.delete_outline_rounded),
                    tooltip: 'Удалить новость',
                  ),
              ],
            ),
            const SizedBox(height: 12),
            Text(item['body'].toString()),
          ],
        ),
      ),
    );
  }
}

class _UserCard extends StatelessWidget {
  const _UserCard({required this.user});

  final JsonMap user;

  @override
  Widget build(BuildContext context) {
    final organization = user['organization'] as JsonMap?;

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: appInsetColor(context),
          borderRadius: BorderRadius.circular(18),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              user['full_name'].toString(),
              style: TextStyle(
                color: appTextColor(context),
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 6),
            Text('УИН: ${user['uin']} · УАН: ${user['uan']}'),
            const SizedBox(height: 4),
            Text(
              'Права: ${user['permissions_label']} · Логин: ${user['login']}',
            ),
            const SizedBox(height: 4),
            Text(
              'Ratubles: ${user['ratubles']} · Организация: ${organization?['name'] ?? 'нет'}',
            ),
            const SizedBox(height: 4),
            Text('Должность: ${user['position_title']}'),
          ],
        ),
      ),
    );
  }
}

class _AdminLogTile extends StatelessWidget {
  const _AdminLogTile({required this.entry});

  final JsonMap entry;

  @override
  Widget build(BuildContext context) {
    final reason = entry['reason']?.toString().trim() ?? '';

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: appInsetColor(context),
          borderRadius: BorderRadius.circular(18),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              entry['summary'].toString(),
              style: TextStyle(
                color: appTextColor(context),
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              'Исполнитель: ${entry['actor_name']}'
              '${entry['target_name'] != null ? ' · Цель: ${entry['target_name']}' : ''}',
              style: TextStyle(color: appMutedTextColor(context, 0.78)),
            ),
            if (reason.isNotEmpty) ...[
              const SizedBox(height: 4),
              Text(
                'Причина: $reason',
                style: TextStyle(color: appMutedTextColor(context, 0.82)),
              ),
            ],
            const SizedBox(height: 4),
            Text(
              formatTimestamp(entry['created_at']),
              style: TextStyle(color: appMutedTextColor(context, 0.68)),
            ),
          ],
        ),
      ),
    );
  }
}

class _RatublesTransactionTile extends StatelessWidget {
  const _RatublesTransactionTile({required this.transaction});

  final JsonMap transaction;

  @override
  Widget build(BuildContext context) {
    final direction = transaction['direction']?.toString() ?? 'neutral';
    final kind = transaction['kind']?.toString() ?? 'transfer';
    final amount = transaction['amount']?.toString() ?? '0';
    final reason = transaction['reason']?.toString() ?? '';
    final senderName = transaction['sender_name']?.toString() ?? 'Неизвестно';
    final senderCode = transaction['sender_code']?.toString();
    final recipientName =
        transaction['recipient_name']?.toString() ?? 'Неизвестно';
    final recipientCode = transaction['recipient_code']?.toString();
    final senderLabel = senderCode == null || senderCode.isEmpty
        ? senderName
        : '$senderName ($senderCode)';
    final recipientLabel = recipientCode == null || recipientCode.isEmpty
        ? recipientName
        : '$recipientName ($recipientCode)';
    final directionLabel = switch ((kind, direction)) {
      ('mint', _) => 'Начисление',
      (_, 'incoming') => 'Входящий перевод',
      (_, 'outgoing') => 'Исходящий перевод',
      _ => 'Транзакция',
    };
    final counterpart = switch ((kind, direction)) {
      ('mint', _) => recipientLabel,
      (_, 'incoming') => senderLabel,
      (_, 'outgoing') => recipientLabel,
      _ => '$senderLabel -> $recipientLabel',
    };

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: appInsetColor(context),
          borderRadius: BorderRadius.circular(18),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  backgroundColor: kind == 'mint' ? moss : sky,
                  foregroundColor: Colors.white,
                  child: Icon(
                    kind == 'mint'
                        ? Icons.add_card_rounded
                        : direction == 'outgoing'
                        ? Icons.north_east_rounded
                        : Icons.south_west_rounded,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '$directionLabel · $amount Ratubles',
                        style: TextStyle(
                          color: appTextColor(context),
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        counterpart,
                        style: TextStyle(
                          color: appMutedTextColor(context, 0.8),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            if (reason.isNotEmpty) ...[
              const SizedBox(height: 10),
              Text(
                'Причина: $reason',
                style: TextStyle(color: appMutedTextColor(context, 0.82)),
              ),
            ],
            const SizedBox(height: 4),
            Text(
              formatTimestamp(transaction['created_at']),
              style: TextStyle(color: appMutedTextColor(context, 0.68)),
            ),
          ],
        ),
      ),
    );
  }
}

class _RatublesLeaderTile extends StatelessWidget {
  const _RatublesLeaderTile({required this.user});

  final JsonMap user;

  @override
  Widget build(BuildContext context) {
    final organization = user['organization'] as JsonMap?;

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: appInsetColor(context),
          borderRadius: BorderRadius.circular(18),
        ),
        child: Row(
          children: [
            CircleAvatar(
              backgroundColor: sky,
              foregroundColor: Colors.white,
              child: Text(initialsFromName(user['full_name'].toString())),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    user['full_name'].toString(),
                    style: TextStyle(
                      color: appTextColor(context),
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${user['permissions_label']} · ${organization?['name'] ?? 'Гражданский сектор'}',
                    style: TextStyle(color: appMutedTextColor(context, 0.75)),
                  ),
                ],
              ),
            ),
            Text(
              '${user['ratubles']}',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                color: copper,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
