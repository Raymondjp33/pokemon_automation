import 'dart:async';

import 'package:flutter/material.dart';
import 'package:socket_io_client/socket_io_client.dart' as io;

import '../models/pokemon.model.dart';
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
  int get rightScreenIndex => streamData?.switch2Content ?? 0;

  final List<String> logs1 = [];

  final List<String> logs2 = [];

  void addToLogs(String line, List<String> logs) {
    logs.add(line);
    if (logs.length > 5) {
      logs.removeAt(0);
    }
  }

  void emitProcess() {
    socket!.emit('start_process', {'file': 'process_test.py'});
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

    socket!.on('process_output', (data) {
      addToLogs('Log: ${data['line']}', logs1);
      // Update UI with log line
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
      pokemonData?.pokemon.where((e) => e.switchNum == 1).toList() ?? [];

  List<PokemonModel> get switch2Pokemon =>
      pokemonData?.pokemon.where((e) => e.switchNum == 2).toList() ?? [];

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
}
