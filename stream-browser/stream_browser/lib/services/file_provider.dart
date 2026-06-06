import 'dart:async';

import 'package:flutter/material.dart';
import 'package:socket_io_client/socket_io_client.dart' as io;

import '../models/display_content.model.dart';
import '../models/pokemon.model.dart';
import '../models/script_info.model.dart';
import '../models/stats.model.dart';
import '../models/stream_data.model.dart';
import '../models/pokemon_data.model.dart';

class FileProvider with ChangeNotifier {
  FileProvider() {
    connectSocket();
    startTimer();
  }

  io.Socket? socket;

  PokemonData? pokemonData;
  StreamData? streamData;
  DateTime now = DateTime.now();

  DisplayContent? get switch1Content => streamData?.switch1Content;
  num get switch1HuntId => switch1Content?.huntId ?? 1;

  DisplayContent? get switch2Content => streamData?.switch2Content;
  num get switch2HuntId => switch2Content?.huntId ?? 1;

  DisplayContent? get switch3Content => streamData?.switch3Content;
  num get switch3HuntId => switch3Content?.huntId ?? 1;

  final List<String> logs1 = [];
  final List<String> logs2 = [];

  List<ScriptInfo> scripts = [];

  Map<String, String> get scriptsByCategory {
    final Map<String, String> map = {};
    for (final s in scripts) {
      map[s.name] = s.category;
    }
    return map;
  }

  void addToLogs(String line, List<String> logs) {
    logs.add(line);
    if (logs.length > 5) {
      logs.removeAt(0);
    }
  }

  void emitProcess() {
    socket!.emit('start_process', {'file': 'process_test.py'});
  }

  void startScript(String name, {int? switchNum, int? startingBox}) {
    final args = <String>[];
    if (switchNum != null) args.addAll(['--switch_num', switchNum.toString()]);
    if (startingBox != null) args.addAll(['--starting_box', startingBox.toString()]);
    socket!.emit('manager_start', {'name': name, 'args': args});
  }

  void stopScript(String name) {
    socket!.emit('manager_stop', {'name': name});
  }

  void sendButton(int switchNum, String button, {double duration = 0.1}) {
    socket!.emit('send_button', {'switch_num': switchNum, 'button': button, 'duration': duration});
  }

  void connectSocket() {
    socket = io.io(
      'http://localhost:5050',
      io.OptionBuilder()
          .setTransports(['websocket'])
          .disableAutoConnect()
          .build(),
    );

    socket!.onConnect((_) {
      print('[Connected] to server');
      socket!.emit('init_connect');
    });

    socket!.on('stream_data', (data) {
      try {
        streamData = StreamData.fromJson(data);
        notifyListeners();
      } catch (e) {
        print('Error with data $e');
      }
    });

    socket!.on('pokemon_data', (data) {
      try {
        pokemonData = PokemonData.fromJson(data);
        notifyListeners();
      } catch (e) {
        print('Error with data $e');
      }
    });

    socket!.on('pokemon_update', (data) {
      try {
        _mergePokemonUpdate(data);
        notifyListeners();
      } catch (e) {
        print('Error with pokemon_update $e');
      }
    });

    socket!.on('manager_status', (data) {
      try {
        scripts = (data['scripts'] as List)
            .map((e) => ScriptInfo.fromJson(e as Map<String, dynamic>))
            .toList();
        notifyListeners();
      } catch (e) {
        print('Error with manager_status $e');
      }
    });

    socket!.on('process_output', (data) {
      addToLogs('Log: ${data['line']}', logs1);
    });

    socket!.on('process_complete', (data) {
      print('Process completed with code: ${data['code']}');
    });

    socket!.onDisconnect((_) => print('[Disconnected]'));

    socket!.connect();
  }

  late Timer timer;
  void startTimer() {
    timer = Timer.periodic(Duration(seconds: 1), (timer) {
      now = DateTime.now();

      if (now.second % 5 == 0) {
        // handleChangeScreenIndex();
      }
      notifyListeners();
    });
  }

  List<PokemonModel> get switch1Pokemon =>
      pokemonData?.pokemon.where((e) => e.huntId == switch1HuntId).toList() ??
      [];

  List<PokemonModel> get switch2Pokemon =>
      pokemonData?.pokemon.where((e) => e.huntId == switch2HuntId).toList() ??
      [];

  List<PokemonModel> get switch3Pokemon =>
      pokemonData?.pokemon.where((e) => e.huntId == switch3HuntId).toList() ??
      [];

  StatsModel? get pokemonStats => pokemonData?.pokemonStats;

  PokemonModel? getPokemonModel(String pokemonName) {
    if (pokemonData == null) {
      return null;
    }

    for (final pokemon in pokemonData!.pokemon) {
      if (pokemonName == pokemon.name) {
        return pokemon;
      }
    }
    return null;
  }

  void _mergePokemonUpdate(dynamic data) {
    if (pokemonData == null) return;

    final updated = (data['pokemon'] as List)
        .map((e) => PokemonModel.fromJson(e as Map<String, dynamic>))
        .toList();

    final merged = List<PokemonModel>.from(pokemonData!.pokemon);
    for (final p in updated) {
      final idx = merged.indexWhere((e) => e.huntId == p.huntId && e.name == p.name);
      if (idx >= 0) {
        merged[idx] = p;
      } else {
        merged.add(p);
      }
    }

    pokemonData = PokemonData(
      pokemon: merged,
      pokemonStats: StatsModel.fromJson(data['pokemonStats'] as Map<String, dynamic>),
    );
  }
}
