# After Branch 35

## Operations and Outputs

User ljyou001 have two followers called oliver and cnn, after ljyou001 posted a tweet,
the Celery output is like this:

```shell
$ celery -A twitter worker -l INFO
bash: warning: setlocale: LC_ALL: cannot change locale (en_US.utf-8)
/usr/lib/python3/dist-packages/requests/__init__.py:80: RequestsDependencyWarning: urllib3 (1.26.16) or chardet (3.0.4) doesn't match a supported version!
  RequestsDependencyWarning)
 
 -------------- celery@50c72a0f9185 v5.1.2 (sun-harmonics)
--- ***** ----- 
-- ******* ---- Linux-6.6.26-linuxkit-x86_64-with-Ubuntu-18.04-bionic 2024-05-17 08:57:34
- *** --- * --- 
- ** ---------- [config]
- ** ---------- .> app:         twitter:0x7ff9c117a240
- ** ---------- .> transport:   redis://127.0.0.1:6379/2
- ** ---------- .> results:     disabled://
- *** --- * --- .> concurrency: 8 (prefork)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** ----- 
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery
                

[tasks]
  . newsfeeds.tasks.fanout_newsfeeds_batch_task
  . newsfeeds.tasks.fanout_newsfeeds_main_task
  . twitter.celery.debug_task

[2024-05-17 08:57:34,666: INFO/MainProcess] Connected to redis://127.0.0.1:6379/2
[2024-05-17 08:57:34,670: INFO/MainProcess] mingle: searching for neighbors
[2024-05-17 08:57:35,678: INFO/MainProcess] mingle: all alone
[2024-05-17 08:57:35,682: WARNING/MainProcess] /home/ljyou001/.local/lib/python3.6/site-packages/celery/fixups/django.py:204: UserWarning: Using settings.DEBUG leads to a memory
            leak, never use this setting in production environments!
  leak, never use this setting in production environments!''')

[2024-05-17 09:03:15,707: INFO/MainProcess] Task newsfeeds.tasks.fanout_newsfeeds_main_task[cc092054-262c-45bc-a22d-0348e103f052] received
(0.000) 
                SELECT VERSION(),
                       @@sql_mode,
                       @@default_storage_engine,
                       @@sql_auto_is_null,
                       @@lower_case_table_names,
                       CONVERT_TZ('2001-01-01 01:00:00', 'UTC', 'UTC') IS NOT NULL
            ; args=None
[2024-05-17 09:03:15,716: DEBUG/ForkPoolWorker-6] (0.000) 
                SELECT VERSION(),
                       @@sql_mode,
                       @@default_storage_engine,
                       @@sql_auto_is_null,
                       @@lower_case_table_names,
                       CONVERT_TZ('2001-01-01 01:00:00', 'UTC', 'UTC') IS NOT NULL
            ; args=None
(0.000) SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED; args=None
[2024-05-17 09:03:15,716: DEBUG/ForkPoolWorker-6] (0.000) SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED; args=None
(0.005) INSERT INTO `newsfeeds_newsfeed` (`user_id`, `tweet_id`, `created_at`) VALUES (1, 2, '2024-05-17 09:03:15.716799'); args=[1, 2, '2024-05-17 09:03:15.716799']
[2024-05-17 09:03:15,722: DEBUG/ForkPoolWorker-6] (0.005) INSERT INTO `newsfeeds_newsfeed` (`user_id`, `tweet_id`, `created_at`) VALUES (1, 2, '2024-05-17 09:03:15.716799'); args=[1, 2, '2024-05-17 09:03:15.716799']
(0.000) SELECT `newsfeeds_newsfeed`.`id`, `newsfeeds_newsfeed`.`user_id`, `newsfeeds_newsfeed`.`tweet_id`, `newsfeeds_newsfeed`.`created_at` FROM `newsfeeds_newsfeed` WHERE `newsfeeds_newsfeed`.`user_id` = 1 ORDER BY `newsfeeds_newsfeed`.`created_at` DESC LIMIT 100; args=(1,)
[2024-05-17 09:03:15,724: DEBUG/ForkPoolWorker-6] (0.000) SELECT `newsfeeds_newsfeed`.`id`, `newsfeeds_newsfeed`.`user_id`, `newsfeeds_newsfeed`.`tweet_id`, `newsfeeds_newsfeed`.`created_at` FROM `newsfeeds_newsfeed` WHERE `newsfeeds_newsfeed`.`user_id` = 1 ORDER BY `newsfeeds_newsfeed`.`created_at` DESC LIMIT 100; args=(1,)
(0.000) SELECT `friendships_friendship`.`id`, `friendships_friendship`.`from_user_id`, `friendships_friendship`.`to_user_id`, `friendships_friendship`.`created_at`, `friendships_friendship`.`updated_at` FROM `friendships_friendship` WHERE `friendships_friendship`.`to_user_id` = 1 ORDER BY `friendships_friendship`.`created_at` DESC; args=(1,)
[2024-05-17 09:03:15,727: DEBUG/ForkPoolWorker-6] (0.000) SELECT `friendships_friendship`.`id`, `friendships_friendship`.`from_user_id`, `friendships_friendship`.`to_user_id`, `friendships_friendship`.`created_at`, `friendships_friendship`.`updated_at` FROM `friendships_friendship` WHERE `friendships_friendship`.`to_user_id` = 1 ORDER BY `friendships_friendship`.`created_at` DESC; args=(1,)
[2024-05-17 09:03:15,738: INFO/MainProcess] Task newsfeeds.tasks.fanout_newsfeeds_batch_task[58f78cf2-8ab9-4200-ad12-56605fa22b34] received
(0.000) 
                SELECT VERSION(),
                       @@sql_mode,
                       @@default_storage_engine,
                       @@sql_auto_is_null,
                       @@lower_case_table_names,
                       CONVERT_TZ('2001-01-01 01:00:00', 'UTC', 'UTC') IS NOT NULL
            ; args=None
[2024-05-17 09:03:15,749: DEBUG/ForkPoolWorker-7] (0.000) 
                SELECT VERSION(),
                       @@sql_mode,
                       @@default_storage_engine,
                       @@sql_auto_is_null,
                       @@lower_case_table_names,
                       CONVERT_TZ('2001-01-01 01:00:00', 'UTC', 'UTC') IS NOT NULL
            ; args=None
(0.000) SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED; args=None
[2024-05-17 09:03:15,749: DEBUG/ForkPoolWorker-7] (0.000) SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED; args=None
(0.000) INSERT INTO `newsfeeds_newsfeed` (`user_id`, `tweet_id`, `created_at`) VALUES (2, 2, '2024-05-17 09:03:15.751617'), (3, 2, '2024-05-17 09:03:15.751711'); args=(2, 2, '2024-05-17 09:03:15.751617', 3, 2, '2024-05-17 09:03:15.751711')
[2024-05-17 09:03:15,752: DEBUG/ForkPoolWorker-7] (0.000) INSERT INTO `newsfeeds_newsfeed` (`user_id`, `tweet_id`, `created_at`) VALUES (2, 2, '2024-05-17 09:03:15.751617'), (3, 2, '2024-05-17 09:03:15.751711'); args=(2, 2, '2024-05-17 09:03:15.751617', 3, 2, '2024-05-17 09:03:15.751711')
(0.000) SELECT `newsfeeds_newsfeed`.`id`, `newsfeeds_newsfeed`.`user_id`, `newsfeeds_newsfeed`.`tweet_id`, `newsfeeds_newsfeed`.`created_at` FROM `newsfeeds_newsfeed` WHERE `newsfeeds_newsfeed`.`user_id` = 2 ORDER BY `newsfeeds_newsfeed`.`created_at` DESC LIMIT 100; args=(2,)
[2024-05-17 09:03:15,764: DEBUG/ForkPoolWorker-7] (0.000) SELECT `newsfeeds_newsfeed`.`id`, `newsfeeds_newsfeed`.`user_id`, `newsfeeds_newsfeed`.`tweet_id`, `newsfeeds_newsfeed`.`created_at` FROM `newsfeeds_newsfeed` WHERE `newsfeeds_newsfeed`.`user_id` = 2 ORDER BY `newsfeeds_newsfeed`.`created_at` DESC LIMIT 100; args=(2,)
(0.000) SELECT `newsfeeds_newsfeed`.`id`, `newsfeeds_newsfeed`.`user_id`, `newsfeeds_newsfeed`.`tweet_id`, `newsfeeds_newsfeed`.`created_at` FROM `newsfeeds_newsfeed` WHERE `newsfeeds_newsfeed`.`user_id` = 3 ORDER BY `newsfeeds_newsfeed`.`created_at` DESC LIMIT 100; args=(3,)
[2024-05-17 09:03:15,767: DEBUG/ForkPoolWorker-7] (0.000) SELECT `newsfeeds_newsfeed`.`id`, `newsfeeds_newsfeed`.`user_id`, `newsfeeds_newsfeed`.`tweet_id`, `newsfeeds_newsfeed`.`created_at` FROM `newsfeeds_newsfeed` WHERE `newsfeeds_newsfeed`.`user_id` = 3 ORDER BY `newsfeeds_newsfeed`.`created_at` DESC LIMIT 100; args=(3,)
```

Without DB debug:

```shell
$ celery -A twitter worker -l INFO
bash: warning: setlocale: LC_ALL: cannot change locale (en_US.utf-8)
/usr/lib/python3/dist-packages/requests/__init__.py:80: RequestsDependencyWarning: urllib3 (1.26.16) or chardet (3.0.4) doesn't match a supported version!
  RequestsDependencyWarning)
 
 -------------- celery@50c72a0f9185 v5.1.2 (sun-harmonics)
--- ***** ----- 
-- ******* ---- Linux-6.6.26-linuxkit-x86_64-with-Ubuntu-18.04-bionic 2024-05-17 09:09:06
- *** --- * --- 
- ** ---------- [config]
- ** ---------- .> app:         twitter:0x7fafbfe3a1d0
- ** ---------- .> transport:   redis://127.0.0.1:6379/2
- ** ---------- .> results:     disabled://
- *** --- * --- .> concurrency: 8 (prefork)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** ----- 
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery
                

[tasks]
  . newsfeeds.tasks.fanout_newsfeeds_batch_task
  . newsfeeds.tasks.fanout_newsfeeds_main_task
  . twitter.celery.debug_task

[2024-05-17 09:09:06,198: INFO/MainProcess] Connected to redis://127.0.0.1:6379/2
[2024-05-17 09:09:06,202: INFO/MainProcess] mingle: searching for neighbors
[2024-05-17 09:09:07,210: INFO/MainProcess] mingle: all alone
[2024-05-17 09:09:07,215: WARNING/MainProcess] /home/ljyou001/.local/lib/python3.6/site-packages/celery/fixups/django.py:204: UserWarning: Using settings.DEBUG leads to a memory
            leak, never use this setting in production environments!
  leak, never use this setting in production environments!''')

[2024-05-17 09:09:07,215: INFO/MainProcess] celery@50c72a0f9185 ready.
[2024-05-17 09:09:25,713: INFO/MainProcess] Task newsfeeds.tasks.fanout_newsfeeds_main_task[333196db-98c4-448e-93ec-7d12faf5f634] received
[2024-05-17 09:09:25,741: INFO/ForkPoolWorker-6] Task newsfeeds.tasks.fanout_newsfeeds_main_task[333196db-98c4-448e-93ec-7d12faf5f634] succeeded in 0.027383225999074057s: '2 newsfeeds going to fanout, 1 batches created'
[2024-05-17 09:09:25,741: INFO/MainProcess] Task newsfeeds.tasks.fanout_newsfeeds_batch_task[d7623ce6-0f06-4ebf-bf68-68318094546e] received
[2024-05-17 09:09:25,765: INFO/ForkPoolWorker-7] Task newsfeeds.tasks.fanout_newsfeeds_batch_task[d7623ce6-0f06-4ebf-bf68-68318094546e] succeeded in 0.02305220800008101s: '2 newsfeeds created'
```
