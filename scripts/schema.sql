CREATE TABLE public.commit (
    repoid integer NOT NULL,
    hash character(40) NOT NULL,
    authorid integer,
    reviewerid integer,
    dt timestamp without time zone,
    files integer,
    inserts integer,
    deletes integer
);


--
-- Name: committer; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.committer (
    id integer NOT NULL,
    name character varying,
    email character varying,
    companyid integer
);


--
-- Name: committer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.committer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.committer_id_seq OWNED BY public.committer.id;


--
-- Name: company; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company (
    id integer NOT NULL,
    name character varying
);


--
-- Name: company_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.company_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: company_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.company_id_seq OWNED BY public.company.id;


--
-- Name: repository; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.repository (
    id integer NOT NULL,
    path character varying
);


--
-- Name: repository_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.repository_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: repository_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.repository_id_seq OWNED BY public.repository.id;


--
-- Name: committer id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.committer ALTER COLUMN id SET DEFAULT nextval('public.committer_id_seq'::regclass);


--
-- Name: company id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company ALTER COLUMN id SET DEFAULT nextval('public.company_id_seq'::regclass);


--
-- Name: repository id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repository ALTER COLUMN id SET DEFAULT nextval('public.repository_id_seq'::regclass);


ALTER TABLE ONLY public.committer
    ADD CONSTRAINT committer_pkey PRIMARY KEY (id);


--
-- Name: company company_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company
    ADD CONSTRAINT company_pkey PRIMARY KEY (id);


--
-- Name: commit pk_commit; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commit
    ADD CONSTRAINT pk_commit PRIMARY KEY (repoid, hash);


--
-- Name: repository repository_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.repository
    ADD CONSTRAINT repository_pkey PRIMARY KEY (id);


--
-- Name: commit fk_commit_author; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commit
    ADD CONSTRAINT fk_commit_author FOREIGN KEY (authorid) REFERENCES public.committer(id);


--
-- Name: commit fk_commit_repo; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commit
    ADD CONSTRAINT fk_commit_repo FOREIGN KEY (repoid) REFERENCES public.repository(id);


--
-- Name: commit fk_commit_reviewer; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.commit
    ADD CONSTRAINT fk_commit_reviewer FOREIGN KEY (reviewerid) REFERENCES public.committer(id);


--
-- Name: committer fk_committer_company; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.committer
    ADD CONSTRAINT fk_committer_company FOREIGN KEY (companyid) REFERENCES public.company(id);


create view vw_committers as
select company.name companyname, committer.name, email, sum(inserts) total_inserts,sum(deletes) total_deletes, sum(files) total_files
from company inner join committer on
company.id = committer.companyid
inner join commit on
commit.authorid = committer.id
group by company.name, committer.name, email
order by total_inserts desc, total_deletes desc, total_files desc;

create view vw_company_commits as
select repository.path, company.name, sum(inserts) total_inserts, sum(deletes) total_deletes, sum(files) total_files
from commit
inner join repository on commit.repoid = repository.id
inner join committer on commit.authorid =committer.id
inner join company on committer.companyid = company.id
group by repository.path, company.name
order by total_inserts desc, total_deletes desc, total_files desc;
