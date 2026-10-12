import json

from typer.testing import CliRunner

from ssd_validator.cli import app


def test_cli_saved_log_experimental_flag(tmp_path):
    log = tmp_path / 'TEST_LOG.txt'
    log.write_text('NVME Identify Controller:\nsqes:0x66\ncqes:0x44\nnpss:4\nawun:0\nawupf:0\noacs:6\n',encoding='utf-8')
    runner = CliRunner()
    for experimental in (False,True):
        args = ['actual','review-log','--input',str(log),'--database',str(tmp_path / 'cli.sqlite3')]
        if experimental:
            args.append('--experimental')
        result = runner.invoke(app,args)
        assert result.exit_code == 0, result.output
        report = json.loads(result.output)
        if experimental:
            assert report['validation']['status'] == 'PASS'
            assert report['validation']['authoritative'] is False
        else:
            assert 'validation' not in report


def test_cli_invalid_bundle_is_visible_error(tmp_path):
    log = tmp_path / 'TEST_LOG.txt'
    log.write_text('NVME Identify Controller:\nnpss:4\n',encoding='utf-8')
    result = CliRunner().invoke(app,['actual','review-log','--input',str(log),'--bundle','latest','--experimental','--database',str(tmp_path / 'cli.sqlite3')])
    assert result.exit_code != 0
    assert 'Unknown Bundle' in result.output
