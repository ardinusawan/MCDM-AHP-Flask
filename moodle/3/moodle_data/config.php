<?php  // Moodle configuration file

unset($CFG);
global $CFG;
$CFG = new stdClass();

$CFG->dbtype    = 'mariadb';
$CFG->dblibrary = 'native';
$CFG->dbhost    = 'mariadb';
$CFG->dbname    = 'bitnami_moodle';
$CFG->dbuser    = 'bn_moodle';
$CFG->dbpass    = 'm4E3cpzOCZ';
$CFG->prefix    = 'mdl_';
$CFG->dboptions = array (
  'dbpersist' => 0,
  'dbport' => 3306,
  'dbsocket' => '',
  'dbcollation' => 'utf8_general_ci',
);

if (empty($_SERVER['HTTP_HOST'])) {
 $_SERVER['HTTP_HOST'] = '127.0.0.1:80';
    }

    if (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] == 'on') {
 $CFG->wwwroot   = 'https://' . $_SERVER['HTTP_HOST'];
    } else {
 $CFG->wwwroot   = 'http://' . $_SERVER['HTTP_HOST'];
    };
$CFG->dataroot  = '/bitnami/moodle/moodledata';
$CFG->admin     = 'admin';

$CFG->directorypermissions = 02775;

require_once('/opt/bitnami/moodle' . '/lib/setup.php');

// There is no php closing tag in this file,
// it is intentional because it prevents trailing whitespace problems!
