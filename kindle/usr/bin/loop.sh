#!/bin/sh

ROWN=0
SLEEPTIME=3600
LOGFILE="/tmp/meteogalicia.log"
SSFILE="/mnt/us/linkss/screensavers/00.meteogalicia.png"
ERRORFILE="/mnt/us/linkss/backups/600x800/01.error.png"

print () {
  #if [ "$ROWN" -eq "0" ]; then
  #  eips -c
  #fi
  STRING="[$(date +%H:%M:%S)] $1"
  #eips 0 $ROWN "$STRING"
  echo "$STRING" >> "$LOGFILE"
  #ROWN=$(($ROWN + 1))
  #if [ "$ROWN" -gt "39" ]; then
  #  ROWN=0
  #fi
}

init() {
  rm -f $LOGFILE
  print "INIT COMPLETE"
}

is_not_in_state() {
        return `lipc-get-prop com.lab126.powerd state | grep $1 | wc -l`;
}

program_wakeup() {
        print "WAKE UP IN $1s"
        ERROR=$(lipc-set-prop -i com.lab126.powerd rtcWakeup $1 2>&1)
        if [ "$ERROR" != "" ]; then
          print "ERROR IN WAKEUP"
          print "$ERROR"
        fi
}

do_wakeup() {
        print "DO WAKEUP"
        powerd_test -p
        while is_not_in_state "active"; do
          sleep 1
        done
        print "WAKEUP DONE"
}

do_sleep() {
        print "DO SLEEP"
        powerd_test -p
        while is_not_in_state "screenSaver"; do
          sleep 1
        done
        sleep 5
        eips -g "$SSFILE"
        print "SLEEP DONE"
}

wifienable() {
       	lipc-set-prop com.lab126.wifid enable 1
}

wifidisable() {
       	lipc-set-prop com.lab126.wifid enable 0
}

gprsdisable() {
        lipc-set-prop com.lab126.wan enable 0
}

wifi_not_connected() {
       	return `lipc-get-prop com.lab126.wifid cmState | grep CONNECTED | wc -l`;
}

do_things() {
      print "DO THINGS"
      mntroot rw
      cp -f "$ERRORFILE" "$SSFILE"
      eips -c
      sleep 5
      eips -g "$SSFILE"
      sleep 5
      eips 0 39 "$(date)"
      gprsdisable
      wifienable
      while wifi_not_connected; do
        sleep 1
      done
      BATTERY_LEVEL="$(lipc-get-prop com.lab126.powerd battLevel)"
      URL="http://192.168.1.4:5080/meteogalicia?battery=$BATTERY_LEVEL"
      curl "$URL" > "$SSFILE"
      eips -g "$SSFILE"
      sleep 5
      wifidisable
      mntroot ro
      print "THINGS DONE"
}

do_silent_things() {
      print "DO STEALTHY THINGS"
      mntroot rw
      cp -f "$ERRORFILE" "$SSFILE"
      gprsdisable
      wifienable
      while wifi_not_connected; do
        sleep 1
      done
      BATTERY_LEVEL="$(lipc-get-prop com.lab126.powerd battLevel)"
      URL="http://192.168.1.4:5080/meteogalicia?battery=$BATTERY_LEVEL"
      curl "$URL" > "$SSFILE"
      wifidisable
      mntroot ro
      print "STEALTHY THINGS DONE"
}

wait_for_event() {
      lipc-wait-event com.lab126.powerd $1
}

get_state() {
  echo "$(lipc-get-prop com.lab126.powerd state)"
}

init
while [ 1 -eq 1 ]; do
  print "START LOOP"
  print "$(get_state)"
  if is_not_in_state "active"; then
    do_wakeup
    do_things
    do_sleep
  else
    do_silent_things
  fi
  print "WAITING FOR EVENTS..."
  LAST_EVENT=""
  while [ "$(echo $LAST_EVENT | awk '/readyToSuspend/{print $2}')" != "6" ]; do
    LAST_EVENT="$(lipc-wait-event com.lab126.powerd *)"
    print "$LAST_EVENT"
    #print "$(get_state)"
  done
  program_wakeup $SLEEPTIME
  sleep 10
done
