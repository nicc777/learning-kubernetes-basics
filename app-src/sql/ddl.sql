DROP TABLE public.user_profiles;
CREATE TABLE public.user_profiles (
	uid bigserial NOT NULL,
	user_alias varchar(64) NOT NULL,
	user_email_address varchar(255) NOT NULL,
	account_status int4 NOT NULL DEFAULT 1,
	CONSTRAINT user_profiles_pk PRIMARY KEY (uid),
	CONSTRAINT user_profiles_un_001 UNIQUE (user_email_address)
);

DROP TABLE public.notes;
CREATE TABLE public.notes (
	nid bigserial NOT NULL,
	uid int4 NOT NULL DEFAULT 1,
	note_timestamp int4 NOT NULL,
	note_text text NOT NULL,
	CONSTRAINT notes_pk PRIMARY KEY (nid),
	CONSTRAINT notes_un_01 UNIQUE (uid, note_timestamp),
	CONSTRAINT notes_un_02 UNIQUE (uid, note_text),
	CONSTRAINT notes_fk FOREIGN KEY (uid) REFERENCES user_profiles(uid) ON UPDATE RESTRICT ON DELETE RESTRICT
);