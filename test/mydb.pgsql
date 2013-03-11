--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = off;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET escape_string_warning = off;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: cities; Type: TABLE; Schema: public; Owner: jkotan; Tablespace: 
--

CREATE TABLE cities (
    name character varying(80),
    location point
);


ALTER TABLE public.cities OWNER TO jkotan;

--
-- Name: weather; Type: TABLE; Schema: public; Owner: jkotan; Tablespace: 
--

CREATE TABLE weather (
    city character varying(80),
    temp_lo integer,
    temp_hi integer,
    prcp real,
    date date
);


ALTER TABLE public.weather OWNER TO jkotan;

--
-- Data for Name: cities; Type: TABLE DATA; Schema: public; Owner: jkotan
--

COPY cities (name, location) FROM stdin;
San Francisco	(-194,53)
\.


--
-- Data for Name: weather; Type: TABLE DATA; Schema: public; Owner: jkotan
--

COPY weather (city, temp_lo, temp_hi, prcp, date) FROM stdin;
San Francisco	46	50	0.25	1994-11-27
Hayward	37	54	\N	1994-11-29
San Francisco	43	57	0	1994-11-29
\.


--
-- Name: public; Type: ACL; Schema: -; Owner: jkotan
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM jkotan;
GRANT ALL ON SCHEMA public TO jkotan;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

