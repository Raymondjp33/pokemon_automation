// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'pokemon.model.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PokemonModel _$PokemonModelFromJson(Map<String, dynamic> json) => PokemonModel(
      name: json['name'] as String? ?? '',
      targets: (json['targets'] as num?)?.toInt() ?? 1,
      switchNum: (json['switchNum'] as num?)?.toInt() ?? 1,
      pokemonId: json['pokemon_id'] as String? ?? '1',
      encounters: (json['encounters'] as num?)?.toInt() ?? 0,
      totalDens: (json['total_dens'] as num?)?.toInt() ?? 0,
      startedHuntTimestamp: json['started_hunt_ts'] as num?,
      catches: (json['catches'] as List<dynamic>?)
          ?.map((e) => CatchModel.fromJson(e as Map<String, dynamic>?))
          .toList(),
    );

Map<String, dynamic> _$PokemonModelToJson(PokemonModel instance) =>
    <String, dynamic>{
      'name': instance.name,
      'targets': instance.targets,
      'switchNum': instance.switchNum,
      'encounters': instance.encounters,
      'pokemon_id': instance.pokemonId,
      'total_dens': instance.totalDens,
      'started_hunt_ts': instance.startedHuntTimestamp,
      'catches': instance.catches?.map((e) => e.toJson()).toList(),
    };
