# JMeter API performance checks

`api-performance.jmx` (TC-392) runs seven requests: version → register → login →
list projects → create project → create bug report → retrieve that bug report.
Each loop creates fictional data without think time. No AI requests are made.

Prerequisites: project dependencies in `.venv`, Java 21 and JMeter **5.6.3**.
The default target is **http://127.0.0.1:8148**. Check `java -version` for Java 21.

## Start and identify a disposable server

Use a dedicated PowerShell window in `D:\Portfolio\ai-qa-bug-triage`. If port
8148 is occupied, identify its owner/configuration, preserve it and stop here.
Do not reuse an existing server or inspect an existing database to prove safety.

```powershell
Set-Location D:\Portfolio\ai-qa-bug-triage
if (Get-NetTCPConnection -LocalPort 8148 -State Listen -ErrorAction SilentlyContinue) {
    throw 'Port 8148 is occupied; preserve the existing process.'
}
$run_dir = Join-Path (Get-Location) ('test-results\jmeter-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $run_dir | Out-Null
$env:DATABASE_NAME = Join-Path $run_dir 'disposable.sqlite3'
$env:JWT_SECRET_KEY = & .\.venv\Scripts\python.exe -c 'import secrets; print(secrets.token_urlsafe(48))'
Remove-Item Env:OPENAI_API_KEY -ErrorAction SilentlyContinue
$env:OPENAI_BASE_URL = 'http://127.0.0.1:9/v1'
$env:AI_EVALUATION_ALLOW_LIVE = '0'
$startup = @'
import asyncio, os, socket, sys
from pathlib import Path
db = Path(os.environ['DATABASE_NAME'])
assert db.is_absolute() and not db.exists(), 'Database must be new and absolute'
assert not os.environ.get('OPENAI_API_KEY'), 'Live AI must be disabled'
listener = socket.socket()
listener.bind(('127.0.0.1', 8148))  # Reserve before app/database startup.
listener.listen(128)
def audit(event, args):
    if event == 'sqlite3.connect' and str(args[0]) not in (str(db), ':memory:'):
        raise RuntimeError('Refused non-test database')
    if event == 'socket.connect' and (not isinstance(args[1], tuple) or args[1][0] not in ('127.0.0.1', '::1')):
        raise RuntimeError('External connections disabled')
sys.addaudithook(audit)
from app import database
from app.main import app
import uvicorn
assert database.DATABASE_NAME == str(db) and not db.exists()
print(f'Owned test PID={os.getpid()} DB={db} AI=disabled', flush=True)
server = uvicorn.Server(uvicorn.Config(app, host='127.0.0.1', port=8148, access_log=False))
try:
    asyncio.run(server.serve(sockets=[listener]), loop_factory=asyncio.SelectorEventLoop)
except KeyboardInterrupt:
    pass
finally:
    listener.close()
'@
& .\.venv\Scripts\python.exe -c $startup
```

Wait for `Application startup complete`. The startup checks verify the fresh
absolute database path before the application creates it, print the owned PID
and database path, and block other SQLite files and external connections.

In a second PowerShell window, compare the listener PID with `Owned test PID`
and confirm the startup command/executable before **any** API or JMeter request:

```powershell
$listener = Get-NetTCPConnection -LocalPort 8148 -State Listen
$listener | Format-List LocalAddress,LocalPort,OwningProcess
Get-CimInstance Win32_Process -Filter "ProcessId=$($listener.OwningProcess)" |
    Format-List ProcessId,ExecutablePath,CommandLine
```

If the process or database configuration cannot be verified, do not test.
Keep the startup window open throughout the run.

## Execute and inspect results

Use the second window. Java should be on PATH; adjust the JMeter path if needed.

```powershell
Set-Location D:\Portfolio\ai-qa-bug-triage
java -version
$jmeter = 'D:\Tools\apache-jmeter-5.6.3\bin\jmeter.bat'
$results = Join-Path (Get-Location) ('jmeter\results\' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $results -Force | Out-Null

# Smoke: one user, one loop; seven HTTP samples.
& $jmeter -n -t jmeter/api-performance.jmx -l "$results\smoke.jtl" -j "$results\smoke.log" -e -o "$results\smoke-html"

# Small concurrent run: two users, two loops; 28 HTTP samples.
& $jmeter -n -t jmeter/api-performance.jmx -Jusers=2 -Jramp_up=1 -Jloops=2 -l "$results\load.jtl" -j "$results\load.log" -e -o "$results\load-html"

# Optional timed load: repeat for ten seconds.
& $jmeter -n -t jmeter/api-performance.jmx -Jusers=2 -Jramp_up=1 -Jloops=-1 -Jduration=10 -l "$results\timed.jtl" -j "$results\timed.log" -e -o "$results\timed-html"

# Generate a dashboard later from an existing JTL if needed.
& $jmeter -g "$results\smoke.jtl" -o "$results\smoke-regenerated-html" -j "$results\report.log"

$samples = @(Import-Csv "$results\smoke.jtl")
$failed = @($samples | Where-Object success -ne 'true')
if ($samples.Count -ne 7 -or $failed.Count) {
    $failed | Format-List label,responseCode,responseMessage,failureMessage
    throw 'Smoke failed; inspect results and the JMeter log.'
}
```

HTTP Request Defaults supplies the shared target to all seven requests. The
Thread Group supplies workload settings. Both use JMeter's built-in `__P()`:
`${__P(port,8148)}` uses the supplied `port` property, otherwise `8148`.
For example, `-Jport=8150` overrides that default; it does not verify isolation.

| Property | Default | Usage |
| --- | --- | --- |
| `protocol` | `http` | HTTP protocol |
| `host` | `127.0.0.1` | Target hostname or IP |
| `port` | `8148` | Target port |
| `users` | `1` | Positive user count |
| `ramp_up` | `1` second | Nonnegative ramp-up; keep below the duration |
| `loops` | `1` | Positive loop count, or `-1` for timed repetition |
| `duration` | `30` seconds | Positive deadline; scheduler remains enabled |

In the GUI, edit HTTP Request Defaults for the target and API Workflow for the
workload. Target overrides are permitted only for an explicitly approved,
independently verified disposable staging environment. For example,
`-Jprotocol=https '-Jhost=staging.example.internal' -Jport=443` illustrates syntax;
that hostname is **not an approved destination**. Properties are not proof of
server identity or database isolation. Staging load testing is deferred until
such an environment exists and its identity/isolation have been verified.
Quote dotted host overrides in PowerShell so they are passed as one argument.

Use valid numeric values; there is no custom configuration-validation script.
The default finishes after one loop, with a 30-second scheduler cap. Requests
have 2s connection / 5s response timeouts. The scheduler checks between requests,
so an in-flight request and report generation can extend elapsed wall time.
A timed run may end partway through a workflow. Any HTTP/assertion failure stops
that user's thread, including subsequent loops. Redirects are disabled.

Use fresh JTL names and absent/empty dashboard directories. JMeter can exit **0
with failed assertions**: check sample counts, all seven request labels and
`success` values. CSV `failureMessage` may be blank for some JSON assertion
failures. Open `*-html/index.html` for per-request and overall results.
Throughput is HTTP requests/second; average is mean response time; p95 describes
the slowest 5% boundary. Errors include HTTP and assertion failures. These small
local runs establish neither production capacity nor a performance SLO.

## Stop, share and clean up

Press **Ctrl+C in the server window**, wait for shutdown and confirm its recorded
PID no longer owns port 8148. Stop only this task's server. Share selected JTL,
HTML folders and logs with a note of versions, machine, parameters and results;
review logs and exclude databases, JWT secrets and environment dumps.

```powershell
# Results window: archive selected run output to a new file.
Compress-Archive -Path "$results\*" -DestinationPath "$results.zip"
# Server window, after confirmed shutdown: validate the owned cleanup path.
$owned_dir = [IO.Path]::GetFullPath($run_dir)
$expected_parent = [IO.Path]::GetFullPath((Join-Path (Get-Location) 'test-results'))
if ((Split-Path $owned_dir -Parent) -ne $expected_parent -or
    (Split-Path $owned_dir -Leaf) -notmatch '^jmeter-[0-9a-f]{32}$') {
    throw 'Cleanup target is not the owned disposable directory.'
}
Remove-Item -LiteralPath $owned_dir -Recurse -Force
Remove-Item Env:DATABASE_NAME,Env:JWT_SECRET_KEY,Env:OPENAI_BASE_URL,Env:AI_EVALUATION_ALLOW_LIVE -ErrorAction SilentlyContinue
```

Close the dedicated server shell. Runtime data under `test-results/`, JMeter
results, JTL files and local property files are ignored. Never delete
`bugtriage.db` or any pre-existing database/directory.

## Historical local evidence

User-supplied manual measurements from JMeter 5.6.3 / Java 21 against fresh
SQLite on port 8150; these were not independently verified by Codex:

| Users / ramp-up / loops or duration | Samples | Average | Throughput | Errors |
| --- | ---: | ---: | ---: | ---: |
| 1 / default / 1 loop | 7 | 66 ms | 11.6/s | 0 |
| 5 / 5s / 2 loops | 70 | 57 ms | 14.5/s | 0 |
| 5 / 1s / 10 loops | 350 | 60 ms | 69.0/s | 0 |
| 10 / 2s / 30 loops | 2100 | 61 ms | 142.3/s | 0 |
| 15 / 5s / 120s | 23112 | 76 ms | 192.3/s | 0 |

The last run's reported overall p95/p99 were approximately 254/313 ms. All runs
created fictional data without think time; these are not production-capacity
measurements. Current independent verification is recorded in
[test execution](../docs/test-execution.md#jmeter-finalization--21-october-2026).
