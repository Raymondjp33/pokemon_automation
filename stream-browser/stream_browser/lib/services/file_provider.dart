import 'dart:async';

import 'package:flutter/material.dart';
import 'package:socket_io_client/socket_io_client.dart' as io;

import '../models/pokemon.model.dart';
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

  void handleChangeScreenIndex() {}

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

  ///
  ///     SWITCH 1
  ///
  List<PokemonModel> get switch1PokemonData {
    if (streamData == null || pokemonData == null) {
      return [];
    }

    return pokemonData!.pokemon
        .where(
          (e) => (streamData?.switch1Targets.map((e) => e.name) ?? [])
              .contains(e.name ?? ''),
        )
        .toList();
  }

  List<PokemonModel> get switch1EggPokemon {
    if (streamData == null || pokemonData == null) {
      return [];
    }

    return pokemonData!.pokemon
        .where(
          (e) =>
              (streamData?.switch1Targets.map((e) => e.name) ?? [])
                  .contains(e.name ?? '') ||
              (e.catches ?? [])
                  .any((e) => e.switchUsed == 1 && e.encounterMethod == 'egg'),
        )
        .toList();
  }

  int get switch1TotalShinies => switch1EggPokemon.fold(
        0,
        (prev, element) => prev + (element.catches?.length ?? 0),
      );
  int get switch1TotalEnc => switch1EggPokemon.fold(
        0,
        (previousValue, element) =>
            previousValue + (element.totalEncounters ?? 0),
      );
  double get switch1AverageEnc =>
      switch1TotalEnc / (switch1TotalShinies == 0 ? 1 : switch1TotalShinies);

  int? get switch1StartTime {
    return switch1PokemonData.firstOrNull?.startedHuntTimestamp?.toInt();
  }

  String get switch1GifNumber =>
      streamData?.switch1Targets.firstOrNull?.dexNum ?? '1';

  int get switch1CurrentEncounters =>
      switch1PokemonData.firstOrNull?.totalEncounters ?? 0;

  String get switch1ShinyCounts {
    int? catches = switch1PokemonData.firstOrNull?.catches?.length;
    int? target = streamData?.switch1Targets.firstOrNull?.target;

    if (catches == null || target == null) {
      return '';
    }

    return '$catches/$target';
  }

  ///
  ///     SWITCH 2
  ///
  List<PokemonModel> get switch2PokemonData {
    if (streamData == null || pokemonData == null) {
      return [];
    }

    return pokemonData!.pokemon
        .where(
          (e) => (streamData?.switch2Targets.map((e) => e.name) ?? [])
              .contains(e.name ?? ''),
        )
        .toList();
  }

  List<PokemonModel> get switch2WildPokemon {
    if (streamData == null || pokemonData == null) {
      return [];
    }

    return pokemonData!.pokemon
        .where(
          (e) =>
              (streamData?.switch2Targets.map((e) => e.name) ?? [])
                  .contains(e.name ?? '') ||
              (e.catches ?? [])
                  .any((e) => e.switchUsed == 2 && e.encounterMethod == 'wild'),
        )
        .toList();
  }

  List<PokemonModel> get switch2EggPokemon {
    if (streamData == null || pokemonData == null) {
      return [];
    }

    return pokemonData!.pokemon
        .where(
          (e) =>
              (streamData?.switch2Targets.map((e) => e.name) ?? [])
                  .contains(e.name ?? '') ||
              (e.catches ?? [])
                  .any((e) => e.switchUsed == 2 && e.encounterMethod == 'egg'),
        )
        .toList();
  }

  int get switch2TotalEnc => switch2WildPokemon.fold(
        0,
        (previousValue, element) =>
            previousValue + (element.totalEncounters ?? 0),
      );

  int get switch2TotalShinies => switch2WildPokemon.fold(
        0,
        (prev, element) => prev + (element.catches?.length ?? 0),
      );

  double get switch2AverageEnc =>
      switch2TotalEnc / (switch2TotalShinies == 0 ? 1 : switch2TotalShinies);

  int? get switch2StartTime {
    return switch2PokemonData.firstOrNull?.startedHuntTimestamp?.toInt();
  }

  String get switch2GifNumber =>
      streamData?.switch2Targets.firstOrNull?.dexNum ?? '1';

  int get switch2CurrentEncounters =>
      switch2PokemonData.firstOrNull?.totalEncounters ?? 0;

  int get switch2TotalEggs => switch2EggPokemon.fold(
        0,
        (previousValue, element) =>
            previousValue + (element.totalEncounters ?? 0),
      );

  int get switch2TotalEggShinies => switch2EggPokemon.fold(
        0,
        (prev, element) => prev + (element.catches?.length ?? 0),
      );

  double get switch2AverageEggs =>
      switch2TotalEggs /
      (switch2TotalEggShinies == 0 ? 1 : switch2TotalEggShinies);

  String get switch2ShinyCounts {
    int? catches = switch2PokemonData.firstOrNull?.catches?.length;
    int? target = streamData?.switch2Targets.firstOrNull?.target;

    if (catches == null || target == null) {
      return '';
    }

    return '$catches/$target';
  }
}
