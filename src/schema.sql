CREATE TABLE public.user_experiment_stats (
	user_id int NOT NULL,
	total_experiment_count int NULL,
	mean_experiment_duration numeric NULL,
	favorite_compound int NULL,
	user_name varchar NULL,
	user_email varchar NULL,
	user_signup_date varchar NULL,
	compound_name varchar NULL,
	compound_structure varchar NULL
);
CREATE UNIQUE INDEX user_experiment_stats_user_id_idx ON public.user_experiment_stats (user_id);
